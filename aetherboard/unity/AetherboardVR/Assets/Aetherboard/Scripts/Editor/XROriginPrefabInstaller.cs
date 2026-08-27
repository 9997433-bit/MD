#if UNITY_EDITOR
using System.IO;
using UnityEditor;
using UnityEngine;

namespace Aetherboard.Editor
{
    public static class XROriginPrefabInstaller
    {
        private const string DestPrefabPath = "Assets/Aetherboard/Resources/Aetherboard/XROriginRig.prefab";
        private static readonly string[] CandidatePaths =
        {
            "Packages/com.unity.xr.interaction.toolkit/Runtime/XR/XR Origin (XR Rig).prefab",
            "Packages/com.unity.xr.interaction.toolkit/Samples~/Starter Assets/Prefabs/XR Origin (XR Rig).prefab",
            "Packages/com.unity.xr.interaction.toolkit/Samples~/Starter Assets/Prefabs/XR Origin (Mobile AR).prefab",
        };

        [MenuItem("Aetherboard/Install XR Origin Prefab")]
        public static void Install()
        {
            var sourcePath = FindSourcePrefab();
            if (string.IsNullOrEmpty(sourcePath))
            {
                Debug.LogError(
                    "Aetherboard: 未找到 XRI 的 XR Origin 预制体。\n" +
                    "请确认已安装 XR Interaction Toolkit 3.0+，或通过 " +
                    "Window → Package Manager → XRI → Samples 导入 Starter Assets。");
                return;
            }

            Directory.CreateDirectory("Assets/Aetherboard/Resources/Aetherboard");
            if (File.Exists(DestPrefabPath))
                AssetDatabase.DeleteAsset(DestPrefabPath);

            if (!AssetDatabase.CopyAsset(sourcePath, DestPrefabPath))
            {
                Debug.LogError($"Aetherboard: 复制预制体失败 {sourcePath}");
                return;
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log(
                $"Aetherboard: 已安装官方 XR Origin 到 {DestPrefabPath}\n" +
                "运行时将通过 Resources.Load 自动加载（XRRigFactory Prefab 模式）。");
        }

        [MenuItem("Aetherboard/Install XR Origin Prefab", true)]
        private static bool ValidateInstall() => !Application.isPlaying;

        private static string FindSourcePrefab()
        {
            foreach (var path in CandidatePaths)
            {
                if (File.Exists(path)) return path;
            }

            var guids = AssetDatabase.FindAssets("XR Origin t:Prefab");
            foreach (var guid in guids)
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                if (path.Contains("XR Interaction Toolkit") &&
                    path.Contains("XR Origin", System.StringComparison.OrdinalIgnoreCase))
                    return path;
            }

            return null;
        }
    }
}
#endif
