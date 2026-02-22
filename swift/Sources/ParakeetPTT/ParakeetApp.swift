import SwiftUI

@main
struct ParakeetApp: App {
    var body: some Scene {
        MenuBarExtra("Parakeet PTT", systemImage: "waveform") {
            Text("Loading...")
            Divider()
            Button("Quit") { NSApplication.shared.terminate(nil) }
        }
    }
}
