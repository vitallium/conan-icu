from conan.packager import ConanMultiPackager

if __name__ == "__main__":
    visual_versions = [14]
    builder = ConanMultiPackager(username="vitallium")
    builder.add_common_builds(visual_versions=visual_versions)
    builder.run()
