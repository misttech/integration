<?xml version="1.0" encoding="UTF-8"?>
<manifest>
  <packages>
    <!-- Milestone CTS release. See fuchsia/prebuilts for the canary release -->
    <package name="fuchsia/cts/${platform}"
             path="prebuilt/cts/current_milestone/{{.OS}}-{{.Arch}}"
             platforms="linux-amd64"
             version="git_revision:aa2ee6ea869ecf2b284ffba68cda461cf4848864" />
  </packages>
</manifest>
