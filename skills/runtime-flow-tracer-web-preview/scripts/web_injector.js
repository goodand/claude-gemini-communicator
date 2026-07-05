/**
 * web_injector.js - Browser-injected JavaScript tracer
 * 
 * Injected via Playwright's page.add_init_script() to trace:
 * - Function calls (wrapped prototypes)
 * - Event listeners (addEventListener interception)
 * - Global variable changes (Proxy on window)
 * - Network requests (fetch/XHR interception)
 * - DOM mutations (MutationObserver)
 * 
 * Collected traces are exposed via window.__TRACE_DATA__ for extraction.
 */

(function() {
  'use strict';

  // Avoid double injection
  if (window.__TRACER_INJECTED__) return;
  window.__TRACER_INJECTED__ = true;

  // ============================================================
  // Configuration
  // ============================================================
  const CONFIG = {
    maxTraces: 10000,           // Limit to prevent memory issues
    traceDepth: 50,             // Max call stack depth
    excludePatterns: [          // Functions to skip
      /^(get|set)$/,
      /^(toString|valueOf|toJSON)$/,
      /^__/,                    // Internal functions
      /^\$/,                    // jQuery internals
    ],
    captureArgs: true,          // Capture function arguments
    captureReturnValues: false, // Capture return values (expensive)
    traceDOM: true,             // Track DOM mutations
    traceNetwork: true,         // Track fetch/XHR
    traceEvents: true,          // Track event listeners
  };

  // ============================================================
  // Trace Storage
  // ============================================================
  const traces = {
    calls: [],          // Function calls
    events: [],         // Event listener triggers
    network: [],        // Network requests
    mutations: [],      // DOM mutations
    errors: [],         // Caught errors
    globals: [],        // Global variable changes
  };

  let callSeq = 0;
  let currentDepth = 0;
  const callStack = [];

  // ============================================================
  // Helper Functions
  // ============================================================
  function getTimestamp() {
    return performance.now().toFixed(2);
  }

  function truncate(str, maxLen = 100) {
    if (typeof str !== 'string') {
      try {
        str = JSON.stringify(str);
      } catch (e) {
        str = String(str);
      }
    }
    return str.length > maxLen ? str.substring(0, maxLen) + '...' : str;
  }

  function shouldExclude(name) {
    return CONFIG.excludePatterns.some(pattern => pattern.test(name));
  }

  function safeStringify(obj) {
    try {
      const seen = new WeakSet();
      return JSON.stringify(obj, (key, value) => {
        if (typeof value === 'object' && value !== null) {
          if (seen.has(value)) return '[Circular]';
          seen.add(value);
        }
        if (typeof value === 'function') return '[Function]';
        if (value instanceof HTMLElement) return `[${value.tagName}]`;
        if (value instanceof Event) return `[Event:${value.type}]`;
        return value;
      });
    } catch (e) {
      return '[Unserializable]';
    }
  }

  // ============================================================
  // Function Call Tracing
  // ============================================================
  function wrapFunction(fn, name, context = 'global') {
    if (typeof fn !== 'function' || fn.__traced__) return fn;
    if (shouldExclude(name)) return fn;

    const wrapped = function(...args) {
      if (traces.calls.length >= CONFIG.maxTraces) {
        return fn.apply(this, args);
      }

      callSeq++;
      currentDepth++;
      const caller = callStack[callStack.length - 1] || null;
      callStack.push(name);

      const trace = {
        seq: callSeq,
        ts: getTimestamp(),
        fn: name,
        context: context,
        depth: currentDepth,
        caller: caller,
      };

      if (CONFIG.captureArgs && args.length > 0) {
        trace.args = args.map(a => truncate(a, 50));
      }

      traces.calls.push(trace);

      try {
        const result = fn.apply(this, args);
        if (CONFIG.captureReturnValues && result !== undefined) {
          trace.ret = truncate(result, 50);
        }
        return result;
      } catch (error) {
        trace.error = error.message;
        traces.errors.push({
          seq: callSeq,
          ts: getTimestamp(),
          fn: name,
          error: error.message,
          stack: error.stack?.split('\n').slice(0, 5),
        });
        throw error;
      } finally {
        callStack.pop();
        currentDepth--;
      }
    };

    wrapped.__traced__ = true;
    wrapped.__original__ = fn;
    wrapped.toString = () => fn.toString();

    return wrapped;
  }

  // Wrap object methods
  function wrapObjectMethods(obj, objName) {
    if (!obj || typeof obj !== 'object') return;

    const props = Object.getOwnPropertyNames(obj);
    for (const prop of props) {
      try {
        const descriptor = Object.getOwnPropertyDescriptor(obj, prop);
        if (descriptor && typeof descriptor.value === 'function') {
          obj[prop] = wrapFunction(descriptor.value, `${objName}.${prop}`, objName);
        }
      } catch (e) {
        // Some properties can't be accessed
      }
    }
  }

  // ============================================================
  // Event Listener Tracing
  // ============================================================
  if (CONFIG.traceEvents) {
    const originalAddEventListener = EventTarget.prototype.addEventListener;
    const originalRemoveEventListener = EventTarget.prototype.removeEventListener;

    EventTarget.prototype.addEventListener = function(type, listener, options) {
      if (typeof listener !== 'function') {
        return originalAddEventListener.call(this, type, listener, options);
      }

      const targetName = this.tagName || this.constructor.name || 'unknown';
      const wrappedListener = function(event) {
        if (traces.events.length < CONFIG.maxTraces) {
          callSeq++;
          traces.events.push({
            seq: callSeq,
            ts: getTimestamp(),
            type: type,
            target: targetName,
            eventTarget: event.target?.tagName || 'unknown',
          });
        }
        return listener.call(this, event);
      };

      wrappedListener.__original__ = listener;
      return originalAddEventListener.call(this, type, wrappedListener, options);
    };
  }

  // ============================================================
  // Network Request Tracing
  // ============================================================
  if (CONFIG.traceNetwork) {
    // Wrap fetch
    const originalFetch = window.fetch;
    window.fetch = async function(input, init) {
      callSeq++;
      const url = typeof input === 'string' ? input : input.url;
      const method = init?.method || 'GET';

      const trace = {
        seq: callSeq,
        ts: getTimestamp(),
        type: 'fetch',
        method: method,
        url: truncate(url, 200),
      };

      traces.network.push(trace);

      try {
        const response = await originalFetch.call(this, input, init);
        trace.status = response.status;
        trace.ok = response.ok;
        return response;
      } catch (error) {
        trace.error = error.message;
        throw error;
      }
    };

    // Wrap XMLHttpRequest
    const originalXHROpen = XMLHttpRequest.prototype.open;
    const originalXHRSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(method, url, ...rest) {
      this.__traceInfo__ = { method, url: truncate(url, 200) };
      return originalXHROpen.call(this, method, url, ...rest);
    };

    XMLHttpRequest.prototype.send = function(body) {
      if (this.__traceInfo__ && traces.network.length < CONFIG.maxTraces) {
        callSeq++;
        const trace = {
          seq: callSeq,
          ts: getTimestamp(),
          type: 'xhr',
          method: this.__traceInfo__.method,
          url: this.__traceInfo__.url,
        };

        traces.network.push(trace);

        this.addEventListener('load', () => {
          trace.status = this.status;
          trace.ok = this.status >= 200 && this.status < 300;
        });

        this.addEventListener('error', () => {
          trace.error = 'Network error';
        });
      }

      return originalXHRSend.call(this, body);
    };
  }

  // ============================================================
  // DOM Mutation Tracing
  // ============================================================
  if (CONFIG.traceDOM) {
    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        if (traces.mutations.length >= CONFIG.maxTraces) break;

        callSeq++;
        const trace = {
          seq: callSeq,
          ts: getTimestamp(),
          type: mutation.type,
          target: mutation.target.tagName || 'unknown',
        };

        if (mutation.type === 'attributes') {
          trace.attr = mutation.attributeName;
          trace.value = truncate(mutation.target.getAttribute(mutation.attributeName), 50);
        } else if (mutation.type === 'childList') {
          trace.added = mutation.addedNodes.length;
          trace.removed = mutation.removedNodes.length;
        }

        traces.mutations.push(trace);
      }
    });

    // Start observing after DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        observer.observe(document.body, {
          childList: true,
          attributes: true,
          subtree: true,
          characterData: true,
        });
      });
    } else {
      observer.observe(document.body || document.documentElement, {
        childList: true,
        attributes: true,
        subtree: true,
        characterData: true,
      });
    }
  }

  // ============================================================
  // Global Variable Change Tracking
  // ============================================================
  const trackedGlobals = new Set();

  window.__trackGlobal__ = function(name) {
    if (trackedGlobals.has(name)) return;
    trackedGlobals.add(name);

    let value = window[name];
    Object.defineProperty(window, name, {
      get() {
        return value;
      },
      set(newValue) {
        if (traces.globals.length < CONFIG.maxTraces) {
          callSeq++;
          traces.globals.push({
            seq: callSeq,
            ts: getTimestamp(),
            name: name,
            oldValue: truncate(value),
            newValue: truncate(newValue),
          });
        }
        value = newValue;
      },
      configurable: true,
    });
  };

  // ============================================================
  // Manual Function Wrapping API
  // ============================================================
  window.__traceFunction__ = function(fn, name) {
    return wrapFunction(fn, name || fn.name || 'anonymous');
  };

  window.__traceObject__ = function(obj, name) {
    wrapObjectMethods(obj, name || 'object');
  };

  // ============================================================
  // Data Export API
  // ============================================================
  window.__TRACE_DATA__ = traces;

  window.__getTraceData__ = function() {
    return {
      metadata: {
        url: window.location.href,
        title: document.title,
        timestamp: new Date().toISOString(),
        totalTraces: callSeq,
        config: CONFIG,
      },
      traces: traces,
    };
  };

  window.__clearTraces__ = function() {
    callSeq = 0;
    currentDepth = 0;
    callStack.length = 0;
    traces.calls.length = 0;
    traces.events.length = 0;
    traces.network.length = 0;
    traces.mutations.length = 0;
    traces.errors.length = 0;
    traces.globals.length = 0;
  };

  window.__exportTraces__ = function() {
    const data = window.__getTraceData__();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `trace_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // ============================================================
  // Auto-wrap common frameworks (optional)
  // ============================================================
  window.__autoWrapFrameworks__ = function() {
    // jQuery
    if (window.jQuery) {
      console.log('[Tracer] Wrapping jQuery');
      wrapObjectMethods(window.jQuery.fn, 'jQuery.fn');
    }

    // React (development mode only)
    if (window.React && window.React.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED) {
      console.log('[Tracer] React detected (dev mode)');
    }

    // Vue
    if (window.Vue) {
      console.log('[Tracer] Vue detected');
    }

    // Angular
    if (window.ng) {
      console.log('[Tracer] Angular detected');
    }
  };

  console.log('[Tracer] Injected successfully. Use window.__getTraceData__() to retrieve traces.');
})();
