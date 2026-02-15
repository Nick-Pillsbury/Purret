#!/bin/bash
set -e


echo "Updating system"
sudo apt update && sudo apt upgrade -y


echo "Installing tools"
sudo apt install -y curl htop ufw wireguard
sudo apt update && sudo apt upgrade -y


echo "Installing Docker"
if ! command -v docker &> /dev/null; then
  echo "Installing Docker"
  curl -fsSL https://get.docker.com | sh
else
  echo "Docker already installed, skipping"
fi
sudo usermod -aG docker $USER
sudo apt install -y docker-compose-plugin
sudo apt update && sudo apt upgrade -y


echo "Enabling IP forwarding"
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-wireguard-forward.conf
sudo sysctl --system


echo "Setting up UFW"
sudo ufw allow 22/tcp
sudo ufw allow 51820/udp
sudo ufw --force enable


echo "Creating WireGuard directory"
sudo mkdir -p /etc/wireguard
sudo chmod 700 /etc/wireguard


echo "Creating key directory"
mkdir -p ~/keys
cd ~/keys


# --- Generate or reuse server keys ---
if [ ! -f server_privatekey.txt ]; then
  echo "Generating server keypair"
  wg genkey | tee server_privatekey.txt | wg pubkey > server_publickey.txt
else
  echo "Reusing existing server keys"
fi

SERVER_PRIVATE_KEY=$(cat server_privatekey.txt)

# --- Generate or reuse client keys ---
if [ ! -f client_privatekeys.txt ]; then
  echo "Generating 5 client keypairs"
  for i in {1..5}; do
    wg genkey | tee -a client_privatekeys.txt | wg pubkey >> client_publickeys.txt
  done
else
  echo "Reusing existing client keys"
fi

# Read client public keys into variables
CLIENT1_PUBLIC_KEY=$(sed -n '1p' client_publickeys.txt)
CLIENT2_PUBLIC_KEY=$(sed -n '2p' client_publickeys.txt)
CLIENT3_PUBLIC_KEY=$(sed -n '3p' client_publickeys.txt)
CLIENT4_PUBLIC_KEY=$(sed -n '4p' client_publickeys.txt)
CLIENT5_PUBLIC_KEY=$(sed -n '5p' client_publickeys.txt)

echo "Creating WireGuard config"

sudo tee /etc/wireguard/wg0.conf > /dev/null <<EOF
[Interface]
PrivateKey = $SERVER_PRIVATE_KEY
Address = 10.0.0.1/24
ListenPort = 51820

# Enable routing + NAT (wifi = wlan0)
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -D FORWARD -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o wlan0 -j MASQUERADE

# Client 1
[Peer]
PublicKey = $CLIENT1_PUBLIC_KEY
AllowedIPs = 10.0.0.2/32

# Client 2
[Peer]
PublicKey = $CLIENT2_PUBLIC_KEY
AllowedIPs = 10.0.0.3/32

# Client 3
[Peer]
PublicKey = $CLIENT3_PUBLIC_KEY
AllowedIPs = 10.0.0.4/32

# Client 4
[Peer]
PublicKey = $CLIENT4_PUBLIC_KEY
AllowedIPs = 10.0.0.5/32

# Client 5
[Peer]
PublicKey = $CLIENT5_PUBLIC_KEY
AllowedIPs = 10.0.0.6/32
EOF

sudo chmod 600 /etc/wireguard/wg0.conf
sudo systemctl enable wg-quick@wg0


echo "Generating client config files"
mkdir -p ~/client-configs
cd ~/client-configs

SERVER_PUBLIC_KEY=$(cat ~/keys/server_publickey.txt)

# Read client private keys
CLIENT1_PRIV=$(sed -n '1p' ~/keys/client_privatekeys.txt)
CLIENT2_PRIV=$(sed -n '2p' ~/keys/client_privatekeys.txt)
CLIENT3_PRIV=$(sed -n '3p' ~/keys/client_privatekeys.txt)
CLIENT4_PRIV=$(sed -n '4p' ~/keys/client_privatekeys.txt)
CLIENT5_PRIV=$(sed -n '5p' ~/keys/client_privatekeys.txt)


ENDPOINT="YOUR_PUBLIC_IP:51820"

# Client 1
cat <<EOF > client1.conf
[Interface]
PrivateKey = $CLIENT1_PRIV
Address = 10.0.0.2/24
DNS = 1.1.1.1

[Peer]
PublicKey = $SERVER_PUBLIC_KEY
Endpoint = $ENDPOINT
AllowedIPs = 10.0.0.0/24, 192.168.1.0/24
PersistentKeepalive = 25
EOF

# Client 2
cat <<EOF > client2.conf
[Interface]
PrivateKey = $CLIENT2_PRIV
Address = 10.0.0.3/24
DNS = 1.1.1.1

[Peer]
PublicKey = $SERVER_PUBLIC_KEY
Endpoint = $ENDPOINT
AllowedIPs = 10.0.0.0/24, 192.168.1.0/24
PersistentKeepalive = 25
EOF

# Client 3
cat <<EOF > client3.conf
[Interface]
PrivateKey = $CLIENT3_PRIV
Address = 10.0.0.4/24
DNS = 1.1.1.1

[Peer]
PublicKey = $SERVER_PUBLIC_KEY
Endpoint = $ENDPOINT
AllowedIPs = 10.0.0.0/24, 192.168.1.0/24
PersistentKeepalive = 25
EOF

# Client 4
cat <<EOF > client4.conf
[Interface]
PrivateKey = $CLIENT4_PRIV
Address = 10.0.0.5/24
DNS = 1.1.1.1

[Peer]
PublicKey = $SERVER_PUBLIC_KEY
Endpoint = $ENDPOINT
AllowedIPs = 10.0.0.0/24, 192.168.1.0/24
PersistentKeepalive = 25
EOF

# Client 5
cat <<EOF > client5.conf
[Interface]
PrivateKey = $CLIENT5_PRIV
Address = 10.0.0.6/24
DNS = 1.1.1.1

[Peer]
PublicKey = $SERVER_PUBLIC_KEY
Endpoint = $ENDPOINT
AllowedIPs = 10.0.0.0/24, 192.168.1.0/24
PersistentKeepalive = 25
EOF

echo "Client configs created in ~/client-configs/"




echo "Done! rebooting!"
sudo reboot