<?xml version="1.0" encoding="UTF-8"?>
<manifest>
  <packages>
    <!-- Milestone CTS release. See fuchsia/prebuilts for the canary release -->
    <package name="fuchsia/cts/${platform}"
             path="prebuilt/cts/current_milestone/{{.OS}}-{{.Arch}}"
             platforms="linux-amd64"
             version="git_revision:511b8243fe13fb52f41f4bc4cc5ce12deb8e5e7c" />
  </packages>
</manifest>
