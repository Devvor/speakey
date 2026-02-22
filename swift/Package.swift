// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "ParakeetPTT",
    platforms: [.macOS(.v14)],
    dependencies: [
        .package(
            url: "https://github.com/FluidInference/FluidAudio.git",
            from: "0.12.1"
        ),
    ],
    targets: [
        .executableTarget(
            name: "parakeet-ptt",
            dependencies: [
                .product(name: "FluidAudio", package: "FluidAudio"),
            ],
            path: "Sources/ParakeetPTT",
            linkerSettings: [
                .linkedFramework("AVFoundation"),
                .linkedFramework("CoreGraphics"),
                .linkedFramework("AppKit"),
            ]
        ),
    ]
)
