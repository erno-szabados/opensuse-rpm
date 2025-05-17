# SRPM for building from source and packaging an RPM for RPM-based distros.
# https://docs.fedoraproject.org/en-US/quick-docs/creating-rpm-packages
# Built and maintained by John Boero - boeroboy@gmail.com
# In honor of Seth Vidal https://www.redhat.com/it/blog/thank-you-seth-vidal

# Notes for llama.cpp:
# 1. Tags are currently based on hash - which will not sort asciibetically.
#    We need to declare standard versioning if people want to sort latest releases.
#    In the meantime, YYYYMMDD format will be used.
Name:           llama.cpp-vulkan
Version:        %( date "+%%Y%%m%%d" )
Release:        1%{?dist}
Summary:        CPU Inference of LLaMA model in pure C/C++ (Vulkan)
License:        MIT
Source0:        https://github.com/ggml-org/llama.cpp/archive/refs/heads/master.tar.gz
BuildRequires:  coreutils cmake gcc14-c++ git libstdc++6-devel-gcc14 vulkan-devel
Requires:       libstdc++6 vulkan
URL:            https://github.com/ggml-org/llama.cpp

%define debug_package %{nil}
%define source_date_epoch_from_changelog 0

%description
CPU inference for Meta's Lllama2 models with Vulkan support.
Models are not included in this package and must be downloaded separately.

%prep
%setup -n llama.cpp-master

%build
CC=gcc-14 CXX=g++-14 cmake -B build -DGGML_VULKAN=ON --install-prefix %{buildroot}
cmake --build build --config Release -- -j

%install
cmake --install build --config Release --prefix %{buildroot}/usr

mkdir -p %{buildroot}/usr/lib/systemd/system
%{__cat} <<'EOF'  > %{buildroot}/usr/lib/systemd/system/llama.service
[Unit]
Description=Llama.cpp server, CPU (Vulkan support).
After=syslog.target network.target local-fs.target remote-fs.target nss-lookup.target

[Service]
Type=simple
EnvironmentFile=/etc/sysconfig/llama
ExecStart=/usr/bin/llama-server $LLAMA_ARGS
ExecReload=/bin/kill -s HUP $MAINPID
Restart=never
CapabilityBoundingSet=CAP_IPC_LOCK
AmbientCapabilities=CAP_IPC_LOCK

[Install]
WantedBy=default.target
EOF

mkdir -p %{buildroot}/etc/sysconfig
%{__cat} <<'EOF'  > %{buildroot}/etc/sysconfig/llama
LLAMA_ARGS="--fim-qwen-1.5b-default -ngl 99 --mlock"
EOF

%clean
rm -rf %{buildroot}
rm -rf %{_builddir}/*

%files
%{_bindir}/
%{_libdir}/
%{_includedir}/
/usr/lib/systemd/system/llama.service
%config /etc/sysconfig/llama

%pre

%post

%preun
%postun

%changelog
