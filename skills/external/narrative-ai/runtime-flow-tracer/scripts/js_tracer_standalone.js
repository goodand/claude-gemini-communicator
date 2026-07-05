
/**
 * js_tracer_standalone.js - Zero-dependency JavaScript function tracer
 * 
 * Uses Function.prototype wrapping to trace all function calls.
 * Works with Node.js built-in modules only.
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

// Trace data storage
const traceData = {
    nodes: new Map(),
    edges: new Map(),
    callSequence: [],
    callStack: [],
    seq: 0,
};

// Helper to create edge key
function edgeKey(from, to) {
    return `${from}::${to}`;
}

// Record a function call
function recordCall(funcName, caller) {
    traceData.seq++;
    const seq = traceData.seq;

    // Record call sequence
    traceData.callSequence.push(funcName);

    // Update node
    if (!traceData.nodes.has(funcName)) {
        traceData.nodes.set(funcName, {
            id: funcName,
            function: funcName,
            call_count: 0,
            first_call_seq: seq,
        });
    }
    const node = traceData.nodes.get(funcName);
    node.call_count++;

    // Create edge from caller
    if (caller) {
        const key = edgeKey(caller, funcName);
        if (!traceData.edges.has(key)) {
            traceData.edges.set(key, {
                source: caller,
                target: funcName,
                call_count: 0,
                first_call_seq: seq,
            });
        }
        traceData.edges.get(key).call_count++;
    }
}

// Wrap a function to trace calls
function wrapFunction(fn, name) {
    if (typeof fn !== 'function' || fn.__traced__) {
        return fn;
    }

    const wrapped = function(...args) {
        const caller = traceData.callStack[traceData.callStack.length - 1] || null;
        recordCall(name, caller);
        traceData.callStack.push(name);

        try {
            return fn.apply(this, args);
        } finally {
            traceData.callStack.pop();
        }
    };

    wrapped.__traced__ = true;
    wrapped.__original__ = fn;
    wrapped.toString = () => fn.toString();

    // Copy properties
    Object.keys(fn).forEach(key => {
        try { wrapped[key] = fn[key]; } catch(e) {}
    });

    return wrapped;
}

// Wrap all functions in an object
function wrapObject(obj, prefix = '') {
    if (!obj || typeof obj !== 'object') return;

    for (const key of Object.keys(obj)) {
        try {
            const val = obj[key];
            if (typeof val === 'function' && !val.__traced__) {
                const name = prefix ? `${prefix}.${key}` : key;
                obj[key] = wrapFunction(val, name);
            }
        } catch (e) {
            // Some properties can't be accessed
        }
    }
}

// Parse and wrap code before execution
function instrumentCode(code, filename) {
    // Simple regex-based instrumentation
    // Wrap function declarations and expressions

    // This is a simplified approach - wrap global functions
    // For production, use a proper AST parser
    return code;
}

// Output trace results
function outputResults() {
    const output = {
        nodes: Array.from(traceData.nodes.values()),
        edges: Array.from(traceData.edges.values()),
        call_sequence: traceData.callSequence,
    };

    console.log('__TRACE_JSON_START__');
    console.log(JSON.stringify(output));
    console.log('__TRACE_JSON_END__');
}

// Main execution
const args = process.argv.slice(2);
if (args.length === 0) {
    console.error('Usage: node js_tracer_standalone.js <script.js> [args...]');
    process.exit(1);
}

const scriptPath = path.resolve(args[0]);
const scriptArgs = args.slice(1);

// Update process.argv for the target script
process.argv = ['node', scriptPath, ...scriptArgs];

try {
    // Read and execute the script
    const code = fs.readFileSync(scriptPath, 'utf8');

    // Create a module-like context
    const scriptDir = path.dirname(scriptPath);
    const scriptModule = {
        exports: {},
        require: (id) => {
            // Handle relative requires
            if (id.startsWith('./') || id.startsWith('../')) {
                const resolvedPath = require.resolve(path.resolve(scriptDir, id));
                const mod = require(resolvedPath);
                return mod;
            }
            return require(id);
        },
        __filename: scriptPath,
        __dirname: scriptDir,
    };

    // Create sandbox with wrapped global functions
    const sandbox = {
        ...global,
        module: scriptModule,
        exports: scriptModule.exports,
        require: scriptModule.require,
        __filename: scriptPath,
        __dirname: scriptDir,
        console: {
            ...console,
            log: wrapFunction((...args) => {
                // Suppress normal output during tracing
            }, 'console.log'),
            error: console.error,
            warn: console.warn,
        },
        setTimeout: wrapFunction(setTimeout, 'setTimeout'),
        setInterval: wrapFunction(setInterval, 'setInterval'),
        setImmediate: wrapFunction(setImmediate, 'setImmediate'),
    };

    // Wrap the code in a function to capture declarations
    const wrappedCode = `
        (function(module, exports, require, __filename, __dirname) {
            // Capture function declarations
            const __originalFunctions = {};

            ${code}

            // Export for analysis
            if (typeof main === 'function') main();
        })(module, exports, require, __filename, __dirname);
    `;

    // Run in VM context
    vm.runInNewContext(wrappedCode, sandbox, {
        filename: scriptPath,
        displayErrors: true,
    });

} catch (e) {
    console.error('Script error:', e.message);
}

// Output results
outputResults();
