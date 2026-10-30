import Foundation
import AppKit
import PDFKit
import Vision

guard CommandLine.arguments.count == 4,
      let first = Int(CommandLine.arguments[2]),
      let last = Int(CommandLine.arguments[3]),
      let document = PDFDocument(url: URL(fileURLWithPath: CommandLine.arguments[1])) else {
    fputs("Usage: envy-ocr document.pdf firstPage lastPage\n", stderr)
    exit(1)
}
var output: [[String: Any]] = []
for number in max(1, first)...max(1, last) {
    guard let page = document.page(at: number - 1) else { continue }
    try autoreleasepool {
        let bounds = page.bounds(for: .mediaBox)
        let scale = min(3.0, 2400.0 / max(bounds.width, bounds.height))
        let thumbnail = page.thumbnail(of: NSSize(width: bounds.width * scale, height: bounds.height * scale), for: .mediaBox)
        guard let image = thumbnail.cgImage(forProposedRect: nil, context: nil, hints: nil) else { return }
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = .accurate
        request.usesLanguageCorrection = true
        request.recognitionLanguages = ["en-US"]
        let handler = VNImageRequestHandler(cgImage: image, options: [:])
        try handler.perform([request])
        let text = (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n")
        output.append(["page": number, "text": text])
    }
}
let data = try JSONSerialization.data(withJSONObject: output, options: [.sortedKeys])
FileHandle.standardOutput.write(data)
