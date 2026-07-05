import AppKit
import Foundation

private let backendName = "apple_vision_recognize_documents_request"
private let helperRole = "table_structure_hint_sidecar"
private let ownershipSkill = "parser-sidecar-to-canonical-schema-promotion"
private let requiredMacOSMajor = 26
private let xcrunPath = "/usr/bin/xcrun"
private let envInputPath = "VISION_TABLE_HELPER_INPUT_PATH"
private let envOutputPath = "VISION_TABLE_HELPER_OUTPUT_PATH"
private let envSDKPath = "VISION_TABLE_HELPER_SDK_PATH"
private let envSwiftVersion = "VISION_TABLE_HELPER_SWIFT_VERSION"
private let envHostOSVersion = "VISION_TABLE_HELPER_HOST_OS_VERSION"
private let envCompileStatus = "VISION_TABLE_HELPER_COMPILE_STATUS"

struct HelperConfig {
    let inputURL: URL
    let outputURL: URL?
}

struct ProcessResult {
    let exitCode: Int32
    let stdout: Data
    let stderr: Data

    var stdoutString: String {
        String(data: stdout, encoding: .utf8) ?? ""
    }

    var stderrString: String {
        String(data: stderr, encoding: .utf8) ?? ""
    }
}

struct ProbePayload: Codable {
    let sdk_path: String?
    let swift_version: String?
    let host_os_version: String
    let required_macos_major: Int
    let compile_probe_status: String
    let compile_probe_command: [String]
    let compile_probe_exit_code: Int?
    let compile_probe_stderr: String?
}

struct UnsupportedPayload: Codable {
    let status: String
    let backend: String
    let helper_role: String
    let ownership_skill: String
    let input_path: String
    let output_path: String?
    let message: String
    let probe: ProbePayload
}

struct ImagePreprocessInfo {
    let path: String
    let reason: String
}

enum HelperError: Error {
    case missingInput
    case missingValue(String)
    case unknownArgument(String)
    case inputDoesNotExist(String)
}

func printUsage() {
    let usage = """
    Usage:
      xcrun swift skills/parser-sidecar-to-canonical-schema-promotion/scripts/macos_table_structure_helper.swift --input /abs/path/image.png [--output /abs/path/helper.json]

    Behavior:
      - Runs an explicit local Apple Vision SDK probe before attempting document/table extraction.
      - Emits machine-readable JSON to stdout on success and on unsupported states.
      - If --output is provided, writes the same JSON payload to that path in addition to stdout.
      - Produces helper-sidecar output only; it does not normalize into the canonical table schema.
    """
    print(usage)
}

func normalizePath(_ rawPath: String) -> URL {
    let expanded = (rawPath as NSString).expandingTildeInPath
    if expanded.hasPrefix("/") {
        return URL(fileURLWithPath: expanded).standardizedFileURL
    }

    return URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
        .appendingPathComponent(expanded)
        .standardizedFileURL
}

func parseArguments() throws -> HelperConfig {
    var inputPath: String?
    var outputPath: String?

    let args = Array(CommandLine.arguments.dropFirst())
    var index = 0

    while index < args.count {
        let arg = args[index]
        switch arg {
        case "--help", "-h":
            printUsage()
            Foundation.exit(EXIT_SUCCESS)
        case "--input":
            index += 1
            guard index < args.count else {
                throw HelperError.missingValue("--input")
            }
            inputPath = args[index]
        case "--output":
            index += 1
            guard index < args.count else {
                throw HelperError.missingValue("--output")
            }
            outputPath = args[index]
        default:
            throw HelperError.unknownArgument(arg)
        }
        index += 1
    }

    guard let inputPath else {
        throw HelperError.missingInput
    }

    let inputURL = normalizePath(inputPath)
    guard FileManager.default.fileExists(atPath: inputURL.path) else {
        throw HelperError.inputDoesNotExist(inputURL.path)
    }

    return HelperConfig(
        inputURL: inputURL,
        outputURL: outputPath.map(normalizePath)
    )
}

func runProcess(_ executablePath: String, arguments: [String], environment: [String: String]? = nil) throws -> ProcessResult {
    let process = Process()
    process.executableURL = URL(fileURLWithPath: executablePath)
    process.arguments = arguments

    var mergedEnvironment = ProcessInfo.processInfo.environment
    if let environment {
        mergedEnvironment.merge(environment) { _, new in new }
    }
    process.environment = mergedEnvironment

    let stdoutPipe = Pipe()
    let stderrPipe = Pipe()
    process.standardOutput = stdoutPipe
    process.standardError = stderrPipe

    try process.run()
    process.waitUntilExit()

    return ProcessResult(
        exitCode: process.terminationStatus,
        stdout: stdoutPipe.fileHandleForReading.readDataToEndOfFile(),
        stderr: stderrPipe.fileHandleForReading.readDataToEndOfFile()
    )
}

func trimmedOrNil(_ value: String?) -> String? {
    guard let value else {
        return nil
    }

    let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
    return trimmed.isEmpty ? nil : trimmed
}

func osVersionString() -> String {
    let version = ProcessInfo.processInfo.operatingSystemVersion
    return "\(version.majorVersion).\(version.minorVersion).\(version.patchVersion)"
}

func currentOSSupportsRecognizeDocumentsRequest() -> Bool {
    ProcessInfo.processInfo.operatingSystemVersion.majorVersion >= requiredMacOSMajor
}

func truncate(_ value: String?, maxLength: Int = 4000) -> String? {
    guard let value = trimmedOrNil(value) else {
        return nil
    }

    if value.count <= maxLength {
        return value
    }

    let endIndex = value.index(value.startIndex, offsetBy: maxLength)
    return String(value[..<endIndex]) + "\n...truncated..."
}

func emitJSONData(_ data: Data, outputURL: URL?) throws {
    if let outputURL {
        let parentDirectory = outputURL.deletingLastPathComponent()
        try FileManager.default.createDirectory(at: parentDirectory, withIntermediateDirectories: true)
        try data.write(to: outputURL)
    }

    FileHandle.standardOutput.write(data)
    if data.last != 0x0A {
        FileHandle.standardOutput.write(Data("\n".utf8))
    }
}

func extractFirstJSONObjectData(from data: Data) -> Data? {
    guard let text = String(data: data, encoding: .utf8) else {
        return nil
    }

    guard let startIndex = text.firstIndex(of: "{") else {
        return nil
    }

    var depth = 0
    var inString = false
    var escaping = false

    for index in text[startIndex...].indices {
        let character = text[index]
        if inString {
            if escaping {
                escaping = false
                continue
            }
            if character == "\\" {
                escaping = true
                continue
            }
            if character == "\"" {
                inString = false
            }
            continue
        }

        if character == "\"" {
            inString = true
            continue
        }
        if character == "{" {
            depth += 1
            continue
        }
        if character == "}" {
            depth -= 1
            if depth == 0 {
                let jsonText = String(text[startIndex...index])
                return Data(jsonText.utf8)
            }
        }
    }

    return nil
}

func jsonObject(from data: Data) -> [String: Any]? {
    guard let object = try? JSONSerialization.jsonObject(with: data) else {
        return nil
    }
    return object as? [String: Any]
}

func jsonData(from object: [String: Any]) -> Data? {
    try? JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .sortedKeys])
}

func patchRunnerPayload(
    _ data: Data,
    originalInputPath: String,
    outputPath: String?,
    preprocessInfo: ImagePreprocessInfo? = nil
) -> Data {
    guard var payload = jsonObject(from: data) else {
        return data
    }

    payload["input_path"] = originalInputPath
    if let outputPath {
        payload["output_path"] = outputPath
    }
    if let preprocessInfo {
        payload["preprocessed_input_path"] = preprocessInfo.path
        payload["preprocess_reason"] = preprocessInfo.reason
    }

    return jsonData(from: payload) ?? data
}

func runnerErrorDetailsContainPixelBufferFailure(_ payload: [String: Any]?, result: ProcessResult) -> Bool {
    let outputStrings = [
        payload?["error_detail"] as? String,
        payload?["message"] as? String,
        trimmedOrNil(result.stdoutString),
        trimmedOrNil(result.stderrString),
    ]

    let patterns = [
        "NSOSStatusErrorDomain Code=-6662",
        "Failed to create CVPixelBuffer",
        "CVPixelBuffer",
        "Format = '420f'",
    ]

    for candidate in outputStrings.compactMap({ $0 }) {
        if patterns.contains(where: { candidate.contains($0) }) {
            return true
        }
    }
    return false
}

func writeOpaqueRGBPNG(from inputURL: URL, to outputURL: URL) throws {
    guard let sourceImage = NSImage(contentsOf: inputURL) else {
        throw NSError(
            domain: "VisionTableHelper",
            code: 1001,
            userInfo: [NSLocalizedDescriptionKey: "Failed to load source image for opaque RGB preprocessing."]
        )
    }

    let representation = sourceImage.representations.compactMap { $0 as? NSBitmapImageRep }.first
    let width = max(representation?.pixelsWide ?? Int(sourceImage.size.width.rounded()), 1)
    let height = max(representation?.pixelsHigh ?? Int(sourceImage.size.height.rounded()), 1)

    guard let bitmap = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: width,
        pixelsHigh: height,
        bitsPerSample: 8,
        samplesPerPixel: 3,
        hasAlpha: false,
        isPlanar: false,
        colorSpaceName: .deviceRGB,
        bytesPerRow: 0,
        bitsPerPixel: 0
    ) else {
        throw NSError(
            domain: "VisionTableHelper",
            code: 1002,
            userInfo: [NSLocalizedDescriptionKey: "Failed to allocate RGB bitmap for opaque preprocessing."]
        )
    }

    NSGraphicsContext.saveGraphicsState()
    guard let context = NSGraphicsContext(bitmapImageRep: bitmap) else {
        throw NSError(
            domain: "VisionTableHelper",
            code: 1003,
            userInfo: [NSLocalizedDescriptionKey: "Failed to create graphics context for opaque preprocessing."]
        )
    }
    NSGraphicsContext.current = context
    NSColor.white.setFill()
    NSBezierPath(rect: NSRect(x: 0, y: 0, width: width, height: height)).fill()
    sourceImage.draw(
        in: NSRect(x: 0, y: 0, width: width, height: height),
        from: NSRect.zero,
        operation: .sourceOver,
        fraction: 1.0,
        respectFlipped: true,
        hints: nil
    )
    context.flushGraphics()
    NSGraphicsContext.restoreGraphicsState()

    guard let pngData = bitmap.representation(using: .png, properties: [:]) else {
        throw NSError(
            domain: "VisionTableHelper",
            code: 1004,
            userInfo: [NSLocalizedDescriptionKey: "Failed to encode opaque RGB PNG during preprocessing."]
        )
    }

    try pngData.write(to: outputURL)
}

func emitUnsupportedPayload(
    status: String,
    message: String,
    config: HelperConfig,
    probe: ProbePayload
) throws {
    let payload = UnsupportedPayload(
        status: status,
        backend: backendName,
        helper_role: helperRole,
        ownership_skill: ownershipSkill,
        input_path: config.inputURL.path,
        output_path: config.outputURL?.path,
        message: message,
        probe: probe
    )

    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    let data = try encoder.encode(payload)
    try emitJSONData(data, outputURL: config.outputURL)
}

func readSDKPath() -> String? {
    guard let result = try? runProcess(xcrunPath, arguments: ["--sdk", "macosx", "--show-sdk-path"]) else {
        return nil
    }

    guard result.exitCode == 0 else {
        return nil
    }

    return trimmedOrNil(result.stdoutString)
}

func readSwiftVersion() -> String? {
    guard let result = try? runProcess(xcrunPath, arguments: ["swift", "--version"]) else {
        return nil
    }

    guard result.exitCode == 0 else {
        return nil
    }

    return trimmedOrNil(result.stdoutString)
}

func visionImplementationSource() -> String {
    #"""
    import Foundation
    import Vision

    private let backendName = "apple_vision_recognize_documents_request"
    private let helperRole = "table_structure_hint_sidecar"
    private let ownershipSkill = "parser-sidecar-to-canonical-schema-promotion"
    private let envInputPath = "VISION_TABLE_HELPER_INPUT_PATH"
    private let envOutputPath = "VISION_TABLE_HELPER_OUTPUT_PATH"
    private let envSDKPath = "VISION_TABLE_HELPER_SDK_PATH"
    private let envSwiftVersion = "VISION_TABLE_HELPER_SWIFT_VERSION"
    private let envHostOSVersion = "VISION_TABLE_HELPER_HOST_OS_VERSION"
    private let envCompileStatus = "VISION_TABLE_HELPER_COMPILE_STATUS"

    struct BoundingBoxPayload: Codable {
        let x: Double
        let y: Double
        let width: Double
        let height: Double
    }

    struct RegionPayload: Codable {
        let point_count: Int
        let points: [[Double]]
        let bounding_box: BoundingBoxPayload?
        let area_hint: Double?
    }

    struct LinePayload: Codable {
        let transcript: String
        let confidence: Double
        let bounding_region: RegionPayload?
    }

    struct CellPayload: Codable {
        let row_range: [Int]
        let column_range: [Int]
        let transcript: String
        let line_count: Int
        let line_candidates: [LinePayload]
        let bounding_region: RegionPayload?
    }

    struct TablePayload: Codable {
        let table_index: Int
        let row_count: Int
        let column_count: Int
        let cell_count: Int
        let bounding_region: RegionPayload?
        let cells: [CellPayload]
    }

    struct ParagraphPayload: Codable {
        let paragraph_index: Int
        let transcript: String
        let bounding_region: RegionPayload?
    }

    struct DocumentPayload: Codable {
        let document_index: Int
        let uuid: String
        let confidence: Double
        let title: String?
        let transcript: String
        let paragraph_count: Int
        let table_count: Int
        let barcode_count: Int
        let bounding_region: RegionPayload?
        let paragraphs: [ParagraphPayload]
        let tables: [TablePayload]
    }

    struct SummaryPayload: Codable {
        let document_count: Int
        let table_count: Int
        let cell_count: Int
        let paragraph_count: Int
    }

    struct ProbePayload: Codable {
        let sdk_path: String?
        let swift_version: String?
        let host_os_version: String?
        let required_macos_major: Int
        let compile_probe_status: String
        let supported_revisions: [String]
        let supported_recognition_languages: [String]
    }

    struct SuccessPayload: Codable {
        let status: String
        let backend: String
        let helper_role: String
        let ownership_skill: String
        let input_path: String
        let output_path: String?
        let message: String
        let probe: ProbePayload
        let summary: SummaryPayload
        let documents: [DocumentPayload]
    }

    struct FailurePayload: Codable {
        let status: String
        let backend: String
        let helper_role: String
        let ownership_skill: String
        let input_path: String
        let output_path: String?
        let message: String
        let error_detail: String?
        let probe: ProbePayload
    }

    func environmentValue(_ key: String) -> String? {
        ProcessInfo.processInfo.environment[key]
    }

    func trimmedOrNil(_ value: String?) -> String? {
        guard let value else {
            return nil
        }

        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmed.isEmpty ? nil : trimmed
    }

    func emitJSON<T: Encodable>(_ payload: T) {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]

        do {
            let data = try encoder.encode(payload)
            FileHandle.standardOutput.write(data)
            FileHandle.standardOutput.write(Data("\n".utf8))
        } catch {
            let fallback = "{\"status\":\"encoding_failed\",\"message\":\"\(error.localizedDescription.replacingOccurrences(of: "\"", with: "\\\""))\"}\n"
            FileHandle.standardOutput.write(Data(fallback.utf8))
        }
    }

    func boundingBoxFromPoints(_ points: [[Double]]) -> BoundingBoxPayload? {
        guard let first = points.first, first.count == 2 else {
            return nil
        }

        var minX = first[0]
        var maxX = first[0]
        var minY = first[1]
        var maxY = first[1]

        for point in points.dropFirst() where point.count == 2 {
            minX = min(minX, point[0])
            maxX = max(maxX, point[0])
            minY = min(minY, point[1])
            maxY = max(maxY, point[1])
        }

        return BoundingBoxPayload(
            x: minX,
            y: minY,
            width: maxX - minX,
            height: maxY - minY
        )
    }

    func boundingBoxFromRect(_ rect: CGRect) -> BoundingBoxPayload? {
        guard !rect.isNull else {
            return nil
        }

        let values = [
            rect.origin.x,
            rect.origin.y,
            rect.size.width,
            rect.size.height,
        ]

        guard values.allSatisfy(\.isFinite) else {
            return nil
        }

        return BoundingBoxPayload(
            x: Double(rect.origin.x),
            y: Double(rect.origin.y),
            width: Double(rect.size.width),
            height: Double(rect.size.height)
        )
    }

    func regionPayload(from region: NormalizedRegion) -> RegionPayload? {
        let points = region.normalizedPoints.map { point in
            [Double(point.x), Double(point.y)]
        }

        let boundingBox = boundingBoxFromRect(region.normalizedPath.boundingBox) ?? boundingBoxFromPoints(points)
        let areaHint = points.isEmpty ? nil : region.calculateArea(useOrientedArea: false)

        if points.isEmpty && boundingBox == nil {
            return nil
        }

        return RegionPayload(
            point_count: points.count,
            points: points,
            bounding_box: boundingBox,
            area_hint: areaHint
        )
    }

    func linePayload(from line: RecognizedTextObservation) -> LinePayload {
        let transcript = line.transcript.isEmpty ? (line.topCandidates(1).first?.string ?? "") : line.transcript
        return LinePayload(
            transcript: transcript,
            confidence: Double(line.confidence),
            bounding_region: regionPayload(from: line.boundingRegion)
        )
    }

    func cellPayload(from cell: DocumentObservation.Container.Table.Cell) -> CellPayload {
        let lines = cell.content.text.lines.map(linePayload)
        return CellPayload(
            row_range: [cell.rowRange.lowerBound, cell.rowRange.upperBound],
            column_range: [cell.columnRange.lowerBound, cell.columnRange.upperBound],
            transcript: cell.content.text.transcript,
            line_count: lines.count,
            line_candidates: lines,
            bounding_region: regionPayload(from: cell.content.boundingRegion)
        )
    }

    func tablePayload(from table: DocumentObservation.Container.Table, index: Int) -> TablePayload {
        var uniqueCells: [String: CellPayload] = [:]

        for row in table.rows {
            for cell in row {
                let payload = cellPayload(from: cell)
                let key = "\(payload.row_range[0]):\(payload.row_range[1]):\(payload.column_range[0]):\(payload.column_range[1])"
                if uniqueCells[key] == nil {
                    uniqueCells[key] = payload
                }
            }
        }

        let orderedCells = uniqueCells.values.sorted { lhs, rhs in
            if lhs.row_range[0] != rhs.row_range[0] {
                return lhs.row_range[0] < rhs.row_range[0]
            }
            if lhs.column_range[0] != rhs.column_range[0] {
                return lhs.column_range[0] < rhs.column_range[0]
            }
            if lhs.row_range[1] != rhs.row_range[1] {
                return lhs.row_range[1] < rhs.row_range[1]
            }
            return lhs.column_range[1] < rhs.column_range[1]
        }

        return TablePayload(
            table_index: index,
            row_count: table.rows.count,
            column_count: table.columns.count,
            cell_count: orderedCells.count,
            bounding_region: regionPayload(from: table.boundingRegion),
            cells: orderedCells
        )
    }

    func documentPayload(from document: DocumentObservation, index: Int) -> DocumentPayload {
        let paragraphs = document.document.paragraphs.enumerated().map { paragraphIndex, paragraph in
            ParagraphPayload(
                paragraph_index: paragraphIndex,
                transcript: paragraph.transcript,
                bounding_region: regionPayload(from: paragraph.boundingRegion)
            )
        }

        let tables = document.document.tables.enumerated().map { tableIndex, table in
            tablePayload(from: table, index: tableIndex)
        }

        return DocumentPayload(
            document_index: index,
            uuid: document.uuid.uuidString,
            confidence: Double(document.confidence),
            title: document.document.title?.transcript,
            transcript: document.document.text.transcript,
            paragraph_count: paragraphs.count,
            table_count: tables.count,
            barcode_count: document.document.barcodes.count,
            bounding_region: regionPayload(from: document.document.boundingRegion),
            paragraphs: paragraphs,
            tables: tables
        )
    }

    @main
    enum VisionDocumentRunner {
        static func main() async {
            let inputPath = trimmedOrNil(environmentValue(envInputPath)) ?? ""
            let outputPath = trimmedOrNil(environmentValue(envOutputPath))
            let sdkPath = trimmedOrNil(environmentValue(envSDKPath))
            let swiftVersion = trimmedOrNil(environmentValue(envSwiftVersion))
            let hostOSVersion = trimmedOrNil(environmentValue(envHostOSVersion))
            let compileStatus = trimmedOrNil(environmentValue(envCompileStatus)) ?? "compiled_in_current_sdk"

            var request = RecognizeDocumentsRequest()
            request.textRecognitionOptions.automaticallyDetectLanguage = true
            request.textRecognitionOptions.useLanguageCorrection = true
            request.textRecognitionOptions.maximumCandidateCount = 1
            request.barcodeDetectionOptions.enabled = false

            let probe = ProbePayload(
                sdk_path: sdkPath,
                swift_version: swiftVersion,
                host_os_version: hostOSVersion,
                required_macos_major: 26,
                compile_probe_status: compileStatus,
                supported_revisions: RecognizeDocumentsRequest.supportedRevisions.map { String(describing: $0) }.sorted(),
                supported_recognition_languages: request.supportedRecognitionLanguages.map { String(describing: $0) }.sorted()
            )

            guard !inputPath.isEmpty else {
                emitJSON(FailurePayload(
                    status: "vision_request_failed",
                    backend: backendName,
                    helper_role: helperRole,
                    ownership_skill: ownershipSkill,
                    input_path: inputPath,
                    output_path: outputPath,
                    message: "The helper runner did not receive an input image path.",
                    error_detail: "Missing \(envInputPath) environment variable.",
                    probe: probe
                ))
                return
            }

            let inputURL = URL(fileURLWithPath: inputPath)
            guard FileManager.default.fileExists(atPath: inputURL.path) else {
                emitJSON(FailurePayload(
                    status: "input_image_not_found",
                    backend: backendName,
                    helper_role: helperRole,
                    ownership_skill: ownershipSkill,
                    input_path: inputURL.path,
                    output_path: outputPath,
                    message: "The input image path does not exist on disk.",
                    error_detail: inputURL.path,
                    probe: probe
                ))
                return
            }

            do {
                let handler = ImageRequestHandler(inputURL)
                let observations = try await handler.perform(request)
                let documents = observations.enumerated().map { item in
                    documentPayload(from: item.element, index: item.offset)
                }
                let tableCount = documents.reduce(0) { $0 + $1.table_count }
                let cellCount = documents.flatMap(\.tables).reduce(0) { $0 + $1.cell_count }
                let paragraphCount = documents.reduce(0) { $0 + $1.paragraph_count }
                let summary = SummaryPayload(
                    document_count: documents.count,
                    table_count: tableCount,
                    cell_count: cellCount,
                    paragraph_count: paragraphCount
                )

                let message: String
                if documents.isEmpty {
                    message = "RecognizeDocumentsRequest completed but returned no document observations for the input image."
                } else {
                    message = "RecognizeDocumentsRequest completed successfully and produced helper-sidecar document structure output."
                }

                emitJSON(SuccessPayload(
                    status: "completed",
                    backend: backendName,
                    helper_role: helperRole,
                    ownership_skill: ownershipSkill,
                    input_path: inputURL.path,
                    output_path: outputPath,
                    message: message,
                    probe: probe,
                    summary: summary,
                    documents: documents
                ))
            } catch {
                emitJSON(FailurePayload(
                    status: "vision_request_failed",
                    backend: backendName,
                    helper_role: helperRole,
                    ownership_skill: ownershipSkill,
                    input_path: inputURL.path,
                    output_path: outputPath,
                    message: "RecognizeDocumentsRequest failed while analyzing the input image.",
                    error_detail: error.localizedDescription,
                    probe: probe
                ))
            }
        }
    }
    """#
}

func buildProbePayload(
    sdkPath: String?,
    swiftVersion: String?,
    compileStatus: String,
    compileCommand: [String],
    compileExitCode: Int32?,
    compileStderr: String?
) -> ProbePayload {
    ProbePayload(
        sdk_path: sdkPath,
        swift_version: swiftVersion,
        host_os_version: osVersionString(),
        required_macos_major: requiredMacOSMajor,
        compile_probe_status: compileStatus,
        compile_probe_command: compileCommand,
        compile_probe_exit_code: compileExitCode.map(Int.init),
        compile_probe_stderr: truncate(compileStderr)
    )
}

do {
    let config = try parseArguments()
    let sdkPath = readSDKPath()
    let swiftVersion = readSwiftVersion()

    let tempDirectory = FileManager.default.temporaryDirectory
        .appendingPathComponent("vision-table-helper-\(UUID().uuidString)", isDirectory: true)
    try FileManager.default.createDirectory(at: tempDirectory, withIntermediateDirectories: true)
    defer {
        try? FileManager.default.removeItem(at: tempDirectory)
    }

    let sourceURL = tempDirectory.appendingPathComponent("vision_document_runner.swift")
    let binaryURL = tempDirectory.appendingPathComponent("vision_document_runner")
    try visionImplementationSource().write(to: sourceURL, atomically: true, encoding: .utf8)

    let probeCommand = [
        "swiftc",
        "-parse-as-library",
        "-sdk",
        sdkPath ?? "",
        "-typecheck",
        sourceURL.path,
    ]

    if sdkPath == nil {
        let probe = buildProbePayload(
            sdkPath: sdkPath,
            swiftVersion: swiftVersion,
            compileStatus: "sdk_path_lookup_failed",
            compileCommand: probeCommand,
            compileExitCode: nil,
            compileStderr: "Unable to resolve the active macOS SDK path via xcrun."
        )
        try emitUnsupportedPayload(
            status: "unsupported_in_current_sdk",
            message: "The helper could not resolve a usable macOS SDK for the Apple Vision compile probe.",
            config: config,
            probe: probe
        )
        Foundation.exit(EXIT_SUCCESS)
    }

    let typecheckResult = try runProcess(
        xcrunPath,
        arguments: probeCommand
    )

    if typecheckResult.exitCode != 0 {
        let probe = buildProbePayload(
            sdkPath: sdkPath,
            swiftVersion: swiftVersion,
            compileStatus: "compile_probe_failed",
            compileCommand: probeCommand,
            compileExitCode: typecheckResult.exitCode,
            compileStderr: typecheckResult.stderrString
        )
        try emitUnsupportedPayload(
            status: "unsupported_in_current_sdk",
            message: "The local SDK does not compile the bounded RecognizeDocumentsRequest helper implementation in this workspace.",
            config: config,
            probe: probe
        )
        Foundation.exit(EXIT_SUCCESS)
    }

    if !currentOSSupportsRecognizeDocumentsRequest() {
        let probe = buildProbePayload(
            sdkPath: sdkPath,
            swiftVersion: swiftVersion,
            compileStatus: "compile_probe_succeeded",
            compileCommand: probeCommand,
            compileExitCode: typecheckResult.exitCode,
            compileStderr: typecheckResult.stderrString
        )
        try emitUnsupportedPayload(
            status: "not_available_in_current_os",
            message: "The local SDK compiled the helper, but the current macOS runtime is older than the minimum OS required for RecognizeDocumentsRequest.",
            config: config,
            probe: probe
        )
        Foundation.exit(EXIT_SUCCESS)
    }

    let buildCommand = [
        "swiftc",
        "-parse-as-library",
        "-sdk",
        sdkPath ?? "",
        sourceURL.path,
        "-o",
        binaryURL.path,
    ]
    let buildResult = try runProcess(xcrunPath, arguments: buildCommand)

    if buildResult.exitCode != 0 {
        let probe = buildProbePayload(
            sdkPath: sdkPath,
            swiftVersion: swiftVersion,
            compileStatus: "runner_build_failed",
            compileCommand: buildCommand,
            compileExitCode: buildResult.exitCode,
            compileStderr: buildResult.stderrString
        )
        try emitUnsupportedPayload(
            status: "unsupported_in_current_sdk",
            message: "The compile probe succeeded, but building the bounded Vision helper runner failed in the current workspace.",
            config: config,
            probe: probe
        )
        Foundation.exit(EXIT_SUCCESS)
    }

    let runnerEnvironment = [
        envInputPath: config.inputURL.path,
        envOutputPath: config.outputURL?.path ?? "",
        envSDKPath: sdkPath ?? "",
        envSwiftVersion: swiftVersion ?? "",
        envHostOSVersion: osVersionString(),
        envCompileStatus: "compile_probe_succeeded",
    ]

    let runnerResult = try runProcess(
        binaryURL.path,
        arguments: [],
        environment: runnerEnvironment
    )

    let sanitizedRunnerStdout = extractFirstJSONObjectData(from: runnerResult.stdout) ?? runnerResult.stdout
    let runnerPayload = jsonObject(from: sanitizedRunnerStdout)
    let runnerStatus = runnerPayload?["status"] as? String

    if runnerResult.exitCode == 0,
       runnerStatus == "vision_request_failed",
       runnerErrorDetailsContainPixelBufferFailure(runnerPayload, result: runnerResult) {
        let fallbackImageURL = tempDirectory.appendingPathComponent("vision_input_opaque_rgb.png")
        try writeOpaqueRGBPNG(from: config.inputURL, to: fallbackImageURL)
        var fallbackEnvironment = runnerEnvironment
        fallbackEnvironment[envInputPath] = fallbackImageURL.path
        let fallbackResult = try runProcess(
            binaryURL.path,
            arguments: [],
            environment: fallbackEnvironment
        )
        let sanitizedFallbackStdout = extractFirstJSONObjectData(from: fallbackResult.stdout) ?? fallbackResult.stdout
        guard fallbackResult.exitCode == 0, !sanitizedFallbackStdout.isEmpty else {
            let probe = buildProbePayload(
                sdkPath: sdkPath,
                swiftVersion: swiftVersion,
                compileStatus: "runner_execution_failed",
                compileCommand: buildCommand,
                compileExitCode: fallbackResult.exitCode,
                compileStderr: fallbackResult.stderrString
            )
            try emitUnsupportedPayload(
                status: "unsupported_in_current_sdk",
                message: "The Vision helper runner built successfully, but both the original input and the opaque RGB retry failed in the current workspace.",
                config: config,
                probe: probe
            )
            Foundation.exit(EXIT_SUCCESS)
        }

        let patchedFallbackData = patchRunnerPayload(
            sanitizedFallbackStdout,
            originalInputPath: config.inputURL.path,
            outputPath: config.outputURL?.path,
            preprocessInfo: ImagePreprocessInfo(
                path: fallbackImageURL.path,
                reason: "opaque_rgb_retry_after_cvpixelbuffer_failure"
            )
        )
        try emitJSONData(patchedFallbackData, outputURL: config.outputURL)
        Foundation.exit(EXIT_SUCCESS)
    }

    guard runnerResult.exitCode == 0, !sanitizedRunnerStdout.isEmpty else {
        let probe = buildProbePayload(
            sdkPath: sdkPath,
            swiftVersion: swiftVersion,
            compileStatus: "runner_execution_failed",
            compileCommand: buildCommand,
            compileExitCode: runnerResult.exitCode,
            compileStderr: runnerResult.stderrString
        )
        try emitUnsupportedPayload(
            status: "unsupported_in_current_sdk",
            message: "The Vision helper runner built successfully, but it did not complete cleanly in the current workspace.",
            config: config,
            probe: probe
        )
        Foundation.exit(EXIT_SUCCESS)
    }

    let patchedRunnerData = patchRunnerPayload(
        sanitizedRunnerStdout,
        originalInputPath: config.inputURL.path,
        outputPath: config.outputURL?.path
    )
    try emitJSONData(patchedRunnerData, outputURL: config.outputURL)
} catch HelperError.missingInput {
    fputs("missing required --input argument\n", stderr)
    printUsage()
    Foundation.exit(EXIT_FAILURE)
} catch HelperError.missingValue(let flag) {
    fputs("missing value for \(flag)\n", stderr)
    printUsage()
    Foundation.exit(EXIT_FAILURE)
} catch HelperError.unknownArgument(let argument) {
    fputs("unknown argument: \(argument)\n", stderr)
    printUsage()
    Foundation.exit(EXIT_FAILURE)
} catch HelperError.inputDoesNotExist(let path) {
    fputs("input image does not exist: \(path)\n", stderr)
    Foundation.exit(EXIT_FAILURE)
} catch {
    fputs("unexpected error: \(error.localizedDescription)\n", stderr)
    Foundation.exit(EXIT_FAILURE)
}
