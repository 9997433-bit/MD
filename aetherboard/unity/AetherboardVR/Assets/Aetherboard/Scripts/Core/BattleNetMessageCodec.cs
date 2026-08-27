using System;
using System.Text;

namespace Aetherboard.Core
{
    /// <summary>
    /// Length-prefixed UTF-8 framing for Unity Netcode Custom Messaging compatibility.
    /// </summary>
    public static class BattleNetMessageCodec
    {
        public const int HeaderSize = 4;

        public static byte[] Frame(string json)
        {
            var payload = Encoding.UTF8.GetBytes(json ?? "");
            var buffer = new byte[HeaderSize + payload.Length];
            WriteLength(buffer, payload.Length);
            Buffer.BlockCopy(payload, 0, buffer, HeaderSize, payload.Length);
            return buffer;
        }

        public static string Unframe(byte[] buffer, int length)
        {
            if (buffer == null || length <= HeaderSize) return null;
            var payloadLen = ReadLength(buffer);
            if (payloadLen < 0 || HeaderSize + payloadLen > length) return null;
            return Encoding.UTF8.GetString(buffer, HeaderSize, payloadLen);
        }

        public static int ReadLength(byte[] buffer)
        {
            if (buffer == null || buffer.Length < HeaderSize) return -1;
            return (buffer[0] << 24) | (buffer[1] << 16) | (buffer[2] << 8) | buffer[3];
        }

        private static void WriteLength(byte[] buffer, int length)
        {
            buffer[0] = (byte)((length >> 24) & 0xff);
            buffer[1] = (byte)((length >> 16) & 0xff);
            buffer[2] = (byte)((length >> 8) & 0xff);
            buffer[3] = (byte)(length & 0xff);
        }
    }
}
