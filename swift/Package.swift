// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "Kuaishuo",
    platforms: [.macOS(.v14)],
    dependencies: [
        .package(
            url: "https://github.com/FluidInference/FluidAudio.git",
            from: "0.12.1"
        ),
    ],
    targets: [
        .executableTarget(
            name: "kuaishuo",
            dependencies: [
                .product(name: "FluidAudio", package: "FluidAudio"),
            ],
            path: "Sources/Kuaishuo",
            exclude: ["Info.plist"],
            linkerSettings: [
                .linkedFramework("AVFoundation"),
                .linkedFramework("CoreGraphics"),
                .linkedFramework("AppKit"),
                .linkedFramework("ApplicationServices"),
                .linkedFramework("ServiceManagement"),
            ]
        ),
    ]
)
