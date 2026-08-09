import SwiftUI

@main
struct SpeakeyApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        MenuBarExtra {
            MenuBarView(appState: appDelegate.appState)
        } label: {
            Label("Speakey", systemImage: appDelegate.appState.statusIcon)
                .symbolEffect(.pulse, isActive: appDelegate.appState.isDownloading)
        }
        .menuBarExtraStyle(.window)
    }
}
