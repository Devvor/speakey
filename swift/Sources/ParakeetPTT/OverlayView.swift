import SwiftUI

struct OverlayView: View {
    let status: AppState.Status

    var body: some View {
        HStack(spacing: 10) {
            indicator
            Text(label)
                .font(.system(size: 14, weight: .medium))
                .foregroundStyle(.primary)
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 12)
        .background(.ultraThinMaterial, in: Capsule())
    }

    @ViewBuilder
    private var indicator: some View {
        switch status {
        case .recording:
            Circle()
                .fill(.red)
                .frame(width: 10, height: 10)
        case .transcribing:
            ProgressView()
                .controlSize(.small)
        default:
            EmptyView()
        }
    }

    private var label: String {
        switch status {
        case .recording:    return "Recording..."
        case .transcribing: return "Transcribing..."
        default:            return ""
        }
    }
}
