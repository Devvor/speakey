import SwiftUI

@main
struct ParakeetApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        MenuBarExtra {
            MenuBarView(appState: appDelegate.appState)
        } label: {
            Label("Parakeet PTT", systemImage: appDelegate.appState.statusIcon)
        }
        .menuBarExtraStyle(.window)
    }
}
