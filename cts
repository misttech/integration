<?xml version="1.0" encoding="UTF-8"?>
<manifest>
  <packages>
    <!-- Milestone CTS release. See fuchsia/prebuilts for the canary release -->
    <package name="fuchsia/cts/${platform}"
             path="prebuilt/cts/current_milestone/{{.OS}}-{{.Arch}}"
             platforms="linux-amd64"
             version="git_revision:8e9610cfabf0ac2d6a9db6389fb9075da085427f" />
  </packages>
</manifest>
