import AppKit

enum SystemSettings {
    enum Pane {
        case accessibility
        case microphone

        var url: URL? {
            switch self {
            case .accessibility:
                URL(string: "x-apple.systempreferences:com.apple.settings.PrivacySecurity.extension?Privacy_Accessibility")
            case .microphone:
                URL(string: "x-apple.systempreferences:com.apple.settings.PrivacySecurity.extension?Privacy_Microphone")
            }
        }
    }

    static func open(_ pane: Pane) {
        guard let url = pane.url else { return }
        NSWorkspace.shared.open(url)
    }
}
