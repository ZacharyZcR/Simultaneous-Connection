import socket
import threading
import time


def handle_connection(sock, local_port):
    while True:
        try:
            # 每5秒发送一次心跳包
            message = f"来自端口 {local_port} 的心跳包 - {time.strftime('%H:%M:%S')}"
            print(f"端口 {local_port} 发送: {message}")
            sock.send(message.encode())

            # 接收对方消息
            received = sock.recv(1024).decode()
            print(f"端口 {local_port} 收到: {received}")

            time.sleep(5)

        except socket.error as e:
            print(f"端口 {local_port} 连接断开: {e}")
            break
        except KeyboardInterrupt:
            print(f"端口 {local_port} 收到退出信号")
            break


def connect_endpoint(local_port, remote_port):
    print(f"开始创建端口 {local_port} 的socket")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"绑定本地端口 {local_port}")
    sock.bind(('127.0.0.1', local_port))

    print(f"设置端口 {local_port} 为非阻塞模式")
    sock.setblocking(False)

    print(f"端口 {local_port} 尝试连接到端口 {remote_port}")
    try:
        sock.connect(('127.0.0.1', remote_port))
    except BlockingIOError:
        print(f"端口 {local_port} 的连接进入非阻塞等待状态")
    except Exception as e:
        print(f"端口 {local_port} 连接时发生错误: {e}")

    print(f"端口 {local_port} 等待连接建立...")
    retry_count = 0
    while True:
        try:
            sock.getpeername()
            print(f"端口 {local_port} 成功建立连接到端口 {remote_port}!")
            break
        except socket.error:
            retry_count += 1
            if retry_count % 10 == 0:
                print(f"端口 {local_port} 正在等待连接... (已尝试 {retry_count} 次)")
            time.sleep(0.1)

    # 连接建立后设回阻塞模式
    sock.setblocking(True)

    # 开始处理长连接
    handle_connection(sock, local_port)

    sock.close()
    print(f"端口 {local_port} 关闭连接")


def main():
    print("程序开始运行")
    print("创建两个线程准备同时发起连接...")

    t1 = threading.Thread(target=connect_endpoint, args=(12345, 12346))
    t2 = threading.Thread(target=connect_endpoint, args=(12346, 12345))

    print("启动第一个线程...")
    t1.start()
    print("启动第二个线程...")
    t2.start()

    print("等待连接完成...")
    t1.join()
    t2.join()

    print("程序运行完成!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("程序收到中断信号，准备退出...")
    except Exception as e:
        print(f"程序运行出错: {e}")