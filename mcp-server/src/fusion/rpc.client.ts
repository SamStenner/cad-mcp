import net from 'net';

export class RPCClient {
  constructor(
    private readonly port: number,
    private readonly host: string,
  ) {}

  public send<T = any>(method: string, params?: any): Promise<T> {
    return new Promise((resolve, reject) => {
      const id = `${Date.now()}-${Math.random()}`;
      const payload = JSON.stringify({ id, method, params });

      const socket = new net.Socket();
      let buf = '';
      socket
        .connect(this.port, this.host, () => socket.write(payload))
        .on('data', (c) => (buf += c.toString('utf-8')))
        .on('error', reject)
        .on('close', () => {
          try {
            const msg = JSON.parse(buf.trim());
            if (!msg.ok) return reject(new Error(msg.error));
            resolve(msg.result as T);
          } catch (e) {
            reject(e);
          }
        });
    });
  }
}
