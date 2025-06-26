#!/bin/bash

echo "Criando os FS /docker /kubelet /rancher"

echo -e "o\nn\np\n1\n\n\nt\n8e\nw" | fdisk /dev/sdc
echo -e "o\nn\np\n1\n\n\nt\n8e\nw" | fdisk /dev/sdd
echo -e "o\nn\np\n1\n\n\nt\n8e\nw" | fdisk /dev/sde

pvcreate /dev/sdc1
pvcreate /dev/sdd1
pvcreate /dev/sde1

partprobe /dev/sdc
partprobe /dev/sdd
partprobe /dev/sde

vgcreate dockervg /dev/sdc1
vgcreate kubeletvg /dev/sdd1
vgcreate ranchervg /dev/sde1

lvcreate -l 100%FREE dockervg -n lv_docker
lvcreate -l 100%FREE kubeletvg -n lv_kubelet
lvcreate -l 100%FREE ranchervg -n lv_rancher

# Formatar os discos
mkfs.xfs /dev/mapper/dockervg-lv_docker
mkfs.xfs /dev/mapper/kubeletvg-lv_kubelet
mkfs.xfs /dev/mapper/ranchervg-lv_rancher

# Criar pontos de montagem
mkdir -p /docker
mkdir -p /kubelet
mkdir -p /rancher

# Adicionar ao /etc/fstab para montar automático
echo "/dev/mapper/dockervg-lv_docker /docker xfs defaults 0 0" | tee -a /etc/fstab
echo "/dev/mapper/kubeletvg-lv_kubelet /kubelet xfs defaults 0 0" | tee -a /etc/fstab
echo "/dev/mapper/ranchervg-lv_rancher /rancher xfs defaults 0 0" | tee -a /etc/fstab

# Montar manualmente para testar
mount /docker
mount /kubelet
mount /rancher

echo ""

#========================================================================================

echo "Instalando o Docker"

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Adiciona o repositório oficial do Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Atualiza os repositórios de novo
sudo apt update

# Instala Docker Engine, CLI e containerd
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Configura o Docker para usar /docker como o diretório de dados
# Cria o arquivo de configuração do Docker se não existir
sudo mkdir -p /etc/docker

# Cria ou edita o arquivo daemon.json para apontar para o diretório /docker
echo '{
  "data-root": "/docker"
}' | sudo tee /etc/docker/daemon.json > /dev/null

# Habilita e inicia o serviço Docker
sudo systemctl restart docker
sudo systemctl enable docker
sudo systemctl start docker

# Confirma se o Docker está funcionando
sudo docker version

# Exibe o caminho de armazenamento utilizado pelo Docker
sudo docker info | grep "Docker Root Dir"

echo ""

#========================================================================================

echo "Adicionando a chave ssh"
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINKuYOghaskB4GIPysw4VyHOXnk1bkoMJFvyAdCv2+AA root@joao-Inspiron-348" | sudo tee -a /root/.ssh/authorized_keys
sleep 3
echo "Configurando permissões"
sudo chmod 700 /root/.ssh
sleep 1
sudo chmod 600 /root/.ssh/authorized_keys
sleep 3
echo "Reiniciando sshd"
sudo systemctl restart sshd

ssh-keygen -f '/root/.ssh/known_hosts' -R '192.168.56.81'

ssh root@192.168.56.81 "hostname -i"

echo ""
#========================================================================================

echo "Ajustando horário"
sudo timedatectl set-timezone America/Sao_Paulo
date


#========================================================================================
echo ""
echo "Instalando e Configurando Kubernetes"

set -e

# 1. Atualiza o sistema e instala dependências básicas
sudo apt-get update
sudo apt-get install -y curl gpg

# 2. Remove qualquer resíduo antigo (por segurança, pode rodar sempre)
sudo rm -f /etc/apt/sources.list.d/kubernetes.list
sudo rm -f /usr/share/keyrings/kubernetes-archive-keyring.gpg

# 3. Baixa a chave GPG e converte para o formato correto
sudo curl -fsSLo /tmp/kubernetes-archive-keyring.gpg https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key
sudo gpg --dearmor -o /usr/share/keyrings/kubernetes-archive-keyring.gpg /tmp/kubernetes-archive-keyring.gpg

# 4. Adiciona o repositório oficial Kubernetes
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list

# 5. Atualiza o apt novamente
sudo apt-get update

# 6. Instala kubelet, kubeadm e kubectl
sudo apt-get install -y kubelet kubeadm kubectl

# 7. Impede que sejam atualizados automaticamente
sudo apt-mark hold kubelet kubeadm kubectl

# 8. Configura o kubelet para usar /kubelet como root-dir
sudo mkdir -p /etc/systemd/system/kubelet.service.d
cat <<EOF | sudo tee /etc/systemd/system/kubelet.service.d/99-rootdir.conf
[Service]
Environment="KUBELET_EXTRA_ARGS=--root-dir=/kubelet"
EOF

# 9. Atualiza o systemd
sudo systemctl daemon-reload

# 10. (Não tenta reiniciar kubelet agora porque o cluster ainda não existe)
echo
echo "Configuração do kubelet para usar /kubelet aplicada. O serviço será iniciado após a criação do cluster."

# 11. Exibe as versões instaladas
echo
echo "Instalação concluída! Versões:"
kubeadm version
kubectl version --client
kubelet --version

#========================================================================================

echo ""
echo "Instalando e configurando o Rancher"
sudo docker run -d --restart=unless-stopped \
  -p 80:80 -p 443:443 \
  -v /rancher:/var/lib/rancher \
  --privileged \
  rancher/rancher:latest
