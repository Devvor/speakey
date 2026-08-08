import SwiftUI

struct MenuBarView: View {
    let appState: AppState
    @State private var launchAtLogin = LaunchAtLogin.isEnabled

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

            if case .error = appState.status {
                permissionFixes
            }

            if !appState.lastTranscription.isEmpty {
                Divider()

                Text("Last transcription")
                    .font(.caption)
                    .foregroundStyle(.secondary)

                Text(appState.lastTranscription)
                    .font(.caption)
                    .lineLimit(3)
                    .fixedSize(horizontal: false, vertical: true)

                Button("Copy") {
                    NSPasteboard.general.clearContents()
                    NSPasteboard.general.setString(appState.lastTranscription, forType: .string)
                }
            }

            Divider()

            Toggle("Launch at Login", isOn: $launchAtLogin)
                .toggleStyle(.checkbox)
                .onChange(of: launchAtLogin) { _, enabled in
                    do {
                        try LaunchAtLogin.setEnabled(enabled)
                    } catch {
                        launchAtLogin = LaunchAtLogin.isEnabled
                        print("[PTT] Launch at login failed: \(error.localizedDescription)")
                    }
                }

            Text("Hold fn for 0.3s to record")
                .font(.caption)
                .foregroundStyle(.secondary)

            Divider()

            Button("Quit Parakeet PTT") {
                NSApplication.shared.terminate(nil)
            }
            .keyboardShortcut("q")
        }
        .padding()
        .frame(width: 260)
    }

    @ViewBuilder
    private var permissionFixes: some View {
        Divider()

        Text("Grant permissions, then restart the app.")
            .font(.caption)
            .foregroundStyle(.secondary)

        Button("Open Accessibility Settings") {
            SystemSettings.open(.accessibility)
        }

        Button("Open Microphone Settings") {
            SystemSettings.open(.microphone)
        }

        Button("Open Input Monitoring Settings") {
            SystemSettings.open(.inputMonitoring)
        }
    }
}
