#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

namespace Aetherboard.Editor
{
    public static class NetcodeSetupMenu
    {
        private const string NetcodePackage = "com.unity.netcode.gameobjects";
        private const string TransportPackage = "com.unity.transport";

        [MenuItem("Aetherboard/Netcode/Verify NGO Packages")]
        public static void VerifyNetcodePackages()
        {
            var manifestPath = "Packages/manifest.json";
            var text = System.IO.File.ReadAllText(manifestPath);
            var hasNetcode = text.Contains(NetcodePackage);
            var hasTransport = text.Contains(TransportPackage);

            if (hasNetcode && hasTransport)
            {
                Debug.Log(
                    "Aetherboard: NGO packages present in manifest.json. " +
                    "Add NetworkManager + UnityTransport to your host scene, then Start Host.");
                return;
            }

            Debug.LogWarning(
                "Aetherboard: NGO packages missing from manifest.json. " +
                $"Add \"{NetcodePackage}\" and \"{TransportPackage}\" then reopen the project.");
        }

        [MenuItem("Aetherboard/Netcode/Open Netcode Integration Guide")]
        public static void OpenNetcodeGuide()
        {
            var path = System.IO.Path.GetFullPath(
                System.IO.Path.Combine(Application.dataPath, "../../docs/NETCODE.md"));
            if (System.IO.File.Exists(path)) EditorUtility.RevealInFinder(path);
            else Debug.LogWarning("NETCODE.md not found.");
        }
    }
}
#endif
