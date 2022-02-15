<?xml version="1.0" encoding="UTF-8"?>
<manifest>
  <packages>
    <!-- Milestone CTS release. See fuchsia/prebuilts for the canary release -->
    <package name="fuchsia/cts/${platform}"
             path="prebuilt/cts/current_milestone/{{.OS}}-{{.Arch}}"
             platforms="linux-amd64"
             version="git_revision:5e664b5b412fa3868f6ecc262c637cc55347dded" />
  </packages>
</manifest>
