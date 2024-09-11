<?xml version="1.0" encoding="UTF-8"?>
<manifest>
  <packages>
    <!-- Milestone CTS release. See fuchsia/prebuilts for the canary release -->
    <package name="fuchsia/cts/${platform}"
             path="prebuilt/cts/current_milestone/{{.OS}}-{{.Arch}}"
             platforms="linux-amd64"
             version="git_revision:9f2c51346a38016a44b812d64e2760bcff1154c6" />
  </packages>
</manifest>
