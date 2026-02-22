import SwiftUI

struct MenuBarView: View {
    let appState: AppState

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: appState.statusIcon)
                    .foregroundStyle(appState.isRecording ? .red : .secondary)
                Text(appState.statusText)
                    .font(.headline)
            }

            if appState.isDownloading {
                Text("First launch only.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Divider()

            Text("Hold fn for 0.5s to record")
                .font(.caption)
                .foregroundStyle(.secondary)

            Divider()

            Button("Quit Parakeet PTT") {
                NSApplication.shared.terminate(nil)
            }
            .keyboardShortcut("q")
        }
        .padding()
        .frame(width: 240)
    }
}
