# /// script
# requires-python = "==3.9"
# dependencies = ["quickjs","jsmin"]
# ///

import  quickjs
from jsmin import jsmin
from pathlib import Path

TS1 = """
sequenceDiagram
  title: Sequence Diagram Example
  autonumber
  participant [<actor> User]
  User->>Pintora: Draw me a sequence diagram（with DSL）
  activate Pintora
  Pintora->>Pintora: Parse DSL, draw diagram
  alt DSL is correct
    Pintora->>User: Return the drawn diagram
  else DSL is incorrect
    Pintora->>User: Return error message
  end
  deactivate Pintora
  @note left of Pintora
  Different output formats according to render targets
  1. In browser side. output SVG or Canvas
  2. In Node.js side. output PNG file
  @end_note
"""

TS2 = """
mindmap
@param layoutDirection TB
@param {
  l1NodeBgColor   #2B7A5D
  l1NodeTextColor #fff
  l2NodeBgColor   #26946C
  l2NodeTextColor #fff
  nodeBgColor     #67B599
  textColor       #fff
}
+ UML Diagrams
++ Behavior Diagrams
+++ Sequence Diagram
+++ State Diagram
+++ Activity Diagram
++ Structural Diagrams
+++ Class Diagram
+++ Component Diagram
"""


TS3= """
componentDiagram
  title: Component Diagram Example
  package "@pintora/core" {
    () GraphicsIR
    () IRenderer
    () IDiagram
    [Diagram Registry] as registry
  }
  package "@pintora/diagrams" {
    [...Multiple Diagrams...] as diagrams
    [diagrams]
    [diagrams] --> IDiagram : implements
  }
  package "@pintora/renderer" {
    () "render()" as renderFn
    [SVGRender]
    [CanvasRender]
    [SVGRender] --> IRenderer : implements
    [CanvasRender] --> IRenderer : implements
    IRenderer ..> GraphicsIR : accepts
  }
  package "@pintora/standalone" {
    [standalone]
  }
  [IDiagram] --> GraphicsIR : generate
  [standalone] --> registry : register all of @pintora/diagrams
  [@pintora/standalone] --> [@pintora/diagrams] : import
  [standalone] --> renderFn : call with GraphicsIR

"""


qj = quickjs.Context()
file = []
def qjeval(instr):
    qj.eval(instr)
    file.append(instr)


pintora = Path('runtime.esm.js')
encoding = Path('encoding.js')
encodingIdx = Path('encoding-indexes.js')



qjeval('''
class ConsoleStub {
  constructor() {
    this.logHistory   = [];
    this.errorHistory = [];
    this.warnHistory  = [];
  }

  log(...args) {
    const message = args.join(' ');
    this.logHistory.push(message);
  }

  error(...args) {
    const message = args.join(' ');
    this.errorHistory.push(message);
  }

  warn(...args) {
    const message = args.join(' ');
    this.warnHistory.push(message);
  }
}

var console = new ConsoleStub();




    ''')

import re

qjeval(encodingIdx.read_text(encoding="UTF-8"))
qjeval(encoding.read_text(encoding="UTF-8"))


QJSFIXED = re.sub(r"export\s*\{.*\}","//EXPORTS arn't SUPPORTED",
                pintora.read_text(encoding="UTF-8")
                  .replace("import.meta.url",'""'),
                flags = re.MULTILINE|re.DOTALL)

# Polyfill Uint8Array.fromBase64 (ES2025) which QuickJS does not yet support.
qjeval('''
if (!Uint8Array.fromBase64) {
  Uint8Array.fromBase64 = function(base64) {
    var chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    var lookup = {};
    for (var i = 0; i < chars.length; i++) lookup[chars[i]] = i;
    var clean = base64.replace(/[^A-Za-z0-9+/]/g, "");
    var n = clean.length;
    var bytes = new Uint8Array(Math.ceil(n * 3 / 4));
    var j = 0;
    for (var i = 0; i < n; i += 4) {
      var a = lookup[clean[i]] || 0;
      var b = lookup[clean[i + 1]] || 0;
      var c = lookup[clean[i + 2]] || 0;
      var d = lookup[clean[i + 3]] || 0;
      bytes[j++] = (a << 2) | (b >> 4);
      if (i + 2 < n) bytes[j++] = ((b & 15) << 4) | (c >> 2);
      if (i + 3 < n) bytes[j++] = ((c & 3) << 6) | d;
    }
    return bytes.slice(0, j);
  };
}
''')

# print("\n".join(QJSFIXED.split("\n")[63152:63158]))
qjeval(QJSFIXED)





qjeval("""
    var document = new Document()
    var csrc = document.createElement("div")
    csrc.dataset=[];
    var rslt = document.createElement("svg")

    csrc.dataset['renderer']


    function PintoraRender(e, t = "default", A = "Source Code Pro, sans-serif") {
      csrc.dataset.theme = t;
      var n = config;
      if (n.core.defaultFontFamily = A, configApi.setConfig(n), console = new ConsoleStub, csrc.innerText = e, pintoraStandalone.renderContentOf(csrc, {
          resultContainer: rslt
        }), "" === rslt.innerHTML) throw errorString = "\\n " + String(console.warnHistory.slice(-1)), new Error(errorString);
      return rslt.firstChild.setAttribute("xmlns", "http://www.w3.org/2000/svg"), rslt.innerHTML
    }

    """)
Path("package/pintora.js").write_text(jsmin("\n".join(file)),encoding="UTF-8")



Render=qj.eval("PintoraRender")

print(Render(TS2))

print(qj.eval(""))


# print(Render(TS3))

# print(qj.eval("pintoraStandalone.renderTo(randStr,{container:rslt,config:null})"))

# #look at logs and errors:
# print(qj.eval("console.logHistory.join()"))
# print(qj.eval("console.warnHistory.join()"))
# print(qj.eval("console.errorHistory.join()"))

# # get output
# print(qj.eval("rslt.innerHTML"))
# Path("output.svg").write_text(qj.eval("rslt.innerHTML"),encoding="UTF-8")
