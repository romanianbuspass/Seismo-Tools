pluginManagement {
    val flutterSdkPath =
        run {
            val properties = java.util.Properties()
            file("local.properties").inputStream().use { properties.load(it) }
            val flutterSdkPath = properties.getProperty("flutter.sdk")
            require(flutterSdkPath != null) { "flutter.sdk not set in local.properties" }
            flutterSdkPath
        }

    includeBuild("$flutterSdkPath/packages/flutter_tools/gradle")

    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

plugins {
    id("dev.flutter.flutter-plugin-loader") version "1.0.0"
    id("com.android.application") version "8.11.1" apply false
    id("org.jetbrains.kotlin.android") version "2.2.20" apply false
}

include(":app")

// Fix unmaintained plugins missing 'namespace' and force compileSdk 35
gradle.beforeProject {
    if (project.name != "app" && project.name != rootProject.name) {
        project.afterEvaluate {
            extensions.findByType(com.android.build.gradle.LibraryExtension::class.java)?.let { lib ->
                // Fix missing namespace
                if (lib.namespace.isNullOrEmpty()) {
                    val manifest = project.file("src/main/AndroidManifest.xml")
                    if (manifest.exists()) {
                        val pkg = Regex("""package="([^"]+)"""").find(manifest.readText())?.groupValues?.get(1)
                        if (pkg != null) {
                            lib.namespace = pkg
                        }
                    }
                    if (lib.namespace.isNullOrEmpty()) {
                        lib.namespace = "com.${project.name.replace("-", "_")}"
                    }
                }
                // Force compileSdk 36 (fixes lStar attr in old plugins)
                lib.compileSdk = 36
            }
        }
    }
}
