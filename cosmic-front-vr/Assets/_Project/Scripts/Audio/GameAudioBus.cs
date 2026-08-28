using UnityEngine;

namespace CosmicFront.Audio
{
    /// <summary>
    /// P6 skeleton audio bus. Logs keys until real clips are wired to reserved AudioSources.
    /// </summary>
    public class GameAudioBus : MonoBehaviour
    {
        public static GameAudioBus Instance { get; private set; }

        [SerializeField] private AudioSource oneShotSource;
        [SerializeField] private AudioSource loopSource;

        private string _activeLoopKey;

        public static GameAudioBus EnsureExists()
        {
            if (Instance != null)
            {
                return Instance;
            }

            var existing = FindObjectOfType<GameAudioBus>();
            if (existing != null)
            {
                return existing;
            }

            var go = new GameObject(nameof(GameAudioBus));
            return go.AddComponent<GameAudioBus>();
        }

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }

            Instance = this;
        }

        private void OnDestroy()
        {
            if (Instance == this)
            {
                Instance = null;
            }
        }

        public void PlayOneShot(string key)
        {
            Debug.Log($"[Audio] key={key}");
            // Reserved: map key -> clip, then oneShotSource?.PlayOneShot(clip);
        }

        public void PlayLoop(string key)
        {
            _activeLoopKey = key;
            Debug.Log($"[Audio] key={key}");
            // Reserved: map key -> clip, assign to loopSource, loop = true, Play();
        }

        public void StopLoop(string key)
        {
            if (_activeLoopKey == key)
            {
                _activeLoopKey = null;
            }

            Debug.Log($"[Audio] key={key}");
            // Reserved: if loopSource is playing mapped key, loopSource.Stop();
        }
    }
}
