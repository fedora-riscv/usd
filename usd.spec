%global         __cmake_in_source_build 0
%global         libmajor 0
%global         srcname  USD
%bcond_without  alembic
%bcond_with     documentation
%bcond_without  embree
%bcond_without  imaging
# We must keep jemalloc enabled to work around
# https://github.com/PixarAnimationStudios/USD/issues/1592.
%bcond_without  jemalloc
%bcond_with     openshading
%bcond_with     ocio
%bcond_without  oiio
%bcond_without  python3
%bcond_with     test

Name:           usd
Version:        21.08
Release:        %autorelease
Summary:        3D VFX pipeline interchange file format

# The entire source is ASL 2.0 except:
#
# BSD:
#   - pxr/base/gf/ilmbase_*
#   - pxr/base/js/rapidjson/msinttypes/
#   - pxr/base/tf/pxrDoubleConversion/
#   - pxr/base/tf/pxrLZ4/
# MIT:
#   - pxr/imaging/garch/khrplatform.h
#   - pxr/base/js/rapidjson/, except pxr/base/js/rapidjson/msinttypes/
#   - pxr/base/tf/pyLock.cpp (only some sections; most of the file is
#     ASL 2.0)
#   - third_party/renderman-23/plugin/rmanArgsParser/pugixml/
# MIT or Unlicense:
#   - pxr/imaging/hio/stb/
#
# (Certain build system files are also under licenses other than ASL 2.0, but
# do not contribute their license terms to the built RPMs.)
License:        ASL 2.0 and BSD and MIT and (MIT or Unlicense)
URL:            http://www.openusd.org/
Source0:         https://github.com/PixarAnimationStudios/%{name}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        org.open%{name}.%{name}view.desktop

# https://github.com/PixarAnimationStudios/USD/issues/1387
Patch1:         %{srcname}-20.05-soversion.patch

# https://github.com/PixarAnimationStudios/USD/issues/1591
Patch2:         USD-21.08-OpenEXR3.patch

# Base
BuildRequires:  boost-devel
BuildRequires:  boost-program-options
BuildRequires:  cmake
BuildRequires:  dos2unix
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(blosc)
BuildRequires:  pkgconfig(tbb)

# Documentation
%if %{with documentation}
BuildRequires:  doxygen
BuildRequires:  graphviz
%endif

# For imaging and usd imaging
%if %{with imaging}
%if %{with embree}
BuildRequires:  embree-devel
%endif
%if %{with openshading}
BuildRequires:  openshadinglanguage
BuildRequires:  pkgconfig(oslexec)
%endif
BuildRequires:  opensubdiv-devel
BuildRequires:  openvdb-devel
BuildRequires:  pkgconfig(dri)
%if %{with jemalloc}
BuildRequires:  pkgconfig(jemalloc)
%endif
%if %{with ocio}
# usd is not yet compatible with OpenColorIO 2 so use compat package.
BuildRequires:  pkgconfig(OpenColorIO) < 2
%endif
%if %{with oiio}
BuildRequires:  pkgconfig(OpenImageIO)
%endif
BuildRequires:  cmake(OpenEXR)
BuildRequires:  cmake(Imath)
BuildRequires:  pkgconfig(Ptex)
%endif
%if %{with alembic}
BuildRequires:  cmake(Alembic)
BuildRequires:  hdf5-devel
%endif

Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
%if %{with python3}
Requires:       python3-%{name}%{?_isa} = %{version}-%{release}
%endif

# Upstream bundles
# Filed ticket to convince upstream to use system libraries
# https://github.com/PixarAnimationStudios/USD/issues/1490
Provides:       bundled(double-conversion) = 2.0.0
Provides:       bundled(ilmbase) = 2.5.3
Provides:       bundled(lz4) = 1.9.2
Provides:       bundled(pugixml) = 1.9
Provides:       bundled(rapidjson) = 1.0.2
Provides:       bundled(SPIRV-Reflect) = 1.0
Provides:       bundled(stb_image) = 2.19
Provides:       bundled(stb_image_resize) = 0.95
Provides:       bundled(stb_image_write) = 1.09
Provides:       bundled(VulkanMemoryAllocator) = 3.0.0~development
      
# This package is only available for x86_64
# Will fail to build on other architectures
# https://bugzilla.redhat.com/show_bug.cgi?id=1960848
ExclusiveArch:  x86_64

%description
Universal Scene Description (USD) is a time-sampled scene 
description for interchange between graphics applications.

%package        libs
Summary:        Universal Scene Description library


%description libs
Universal Scene Description (USD) is an efficient, scalable system for
authoring, reading, and streaming time-sampled scene description for
interchange between graphics applications.

%package        devel
Summary:        Development files for USD
Requires:       cmake-filesystem
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description devel
This package contains the C++ header files and symbolic links to the shared
libraries for %{name}. If you would like to develop programs using %{name},
you will need to install %{name}-devel.

# For usdview
%if %{with python3}
%package -n python3-%{name}
Summary: %{summary}

BuildRequires:  desktop-file-utils
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(Qt5)
BuildRequires:  python3dist(jinja2)
BuildRequires:  python3dist(pyside2)
BuildRequires:  python3dist(pyopengl)
Requires:       font(roboto)
Requires:       font(robotoblack)
Requires:       font(robotolight)
Requires:       font(robotomono)
Requires:       python3dist(jinja2)
Requires:       python3dist(pyside2)
Requires:       python3dist(pyopengl)
%py_provides    python3-pxr

%description -n python3-%{name}
Python language bindings for the Universal Scene Description (USD) C++ API
%endif

%if %{with documentation}
%package        doc
Summary:        Documentation for usd
BuildArch:      noarch
      
%description doc
Documentation for the Universal Scene Description (USD) C++ API
%endif

%prep
%autosetup -p1 -n %{srcname}-%{version}

# Convert NOTICE.txt from CRNL line encoding 
dos2unix NOTICE.txt

%if %{with python3}
# Fix all Python shebangs recursively in .
%py3_shebang_fix .
%endif

# Further drop shebangs line for some py files
sed -r -i '1{/^#!/d}' \
        pxr/usd/sdr/shaderParserTestUtils.py \
        pxr/usd/usdUtils/updateSchemaWithSdrNode.py \
        pxr/usdImaging/usdviewq/usdviewApi.py

# Unbundle Google Roboto fonts
rm -rvf pxr/usdImaging/usdviewq/fonts/*
ln -s %{_datadir}/fonts/google-roboto pxr/usdImaging/usdviewq/fonts/Roboto
ln -s %{_datadir}/fonts/google-roboto-mono \
    pxr/usdImaging/usdviewq/fonts/Roboto_Mono

# Use c++17 standard otherwise build fails
sed -i 's|set(CMAKE_CXX_STANDARD 14)|set(CMAKE_CXX_STANDARD 17)|g' \
        cmake/defaults/CXXDefaults.cmake

# Fix libdir installation
sed -i 's|lib/usd|%{_libdir}/usd|g' cmake/macros/Private.cmake
sed -i 's|"lib"|%{_libdir}|g' cmake/macros/Private.cmake
sed -i 's|plugin/usd|%{_libdir}/usd/plugin|g' \
        cmake/macros/Private.cmake
sed -i 's|/python|/python%{python3_version}/site-packages|g' \
        cmake/macros/Private.cmake
sed -i 's|lib/usd|%{_libdir}/usd|g' cmake/macros/Public.cmake
sed -i 's|"lib"|%{_libdir}|g' cmake/macros/Public.cmake
sed -i 's|plugin/usd|%{_libdir}/usd/plugin|g' \
        cmake/macros/Public.cmake
        
# Fix cmake directory destination
sed -i 's|"${CMAKE_INSTALL_PREFIX}"|%{_libdir}/cmake/pxr|g' pxr/CMakeLists.txt


%build
# Fix uic-qt5 use
cat > uic-wrapper <<'EOF'
#!/bin/sh
exec uic-qt5 -g python "$@"
EOF
chmod +x uic-wrapper

# Fix python3 support    
# https://github.com/PixarAnimationStudios/USD/issues/1419    

flags="%{optflags} -Wl,--as-needed -DTBB_SUPPRESS_DEPRECATED_MESSAGES=1" \
# Patch2 was not good enough to get the include path for Imath everywhere it
# was needed. Add it globally.
# https://github.com/PixarAnimationStudios/USD/issues/1591
flags="${flags} $(pkgconf --cflags Imath)"

%cmake \
     -DCMAKE_CXX_FLAGS_RELEASE="${flags}" \
     -DCMAKE_C_FLAGS_RELEASE="${flags}" \
     -DCMAKE_CXX_STANDARD=17 \
     -DCMAKE_EXE_LINKER_FLAGS="-pie" \
     -DCMAKE_SKIP_RPATH=ON \
     -DCMAKE_SKIP_INSTALL_RPATH=ON \
     -DCMAKE_VERBOSE_MAKEFILE=ON \
     -DPXR_BUILD_USDVIEW=ON \
%if %{with documentation}
     -DPXR_BUILD_DOCUMENTATION=TRUE \
%endif
     -DPXR_BUILD_EXAMPLES=OFF \
     -DPXR_BUILD_TUTORIALS=OFF \
     -DPXR_BUILD_TESTS=%{?with_test:ON}%{!?with_test:OFF} \
     -DPXR_ENABLE_OPENVDB_SUPPORT=ON \
     -DPXR_INSTALL_LOCATION="%{_libdir}/%{name}/plugin" \
%if %{with jemalloc}
     -DPXR_MALLOC_LIBRARY="%{_libdir}/libjemalloc.so" \
%endif
%if %{with alembic}
     -DOPENEXR_LOCATION=%{_includedir} \
     -DPXR_BUILD_ALEMBIC_PLUGIN=ON \
%endif
%if %{with embree}
     -DPXR_BUILD_EMBREE_PLUGIN=ON \
     -DEMBREE_LOCATION=%{_prefix} \
%endif
%if %{with ocio}
     -DPXR_BUILD_OPENCOLORIO_PLUGIN=ON \
%endif
%if %{with oiio}
     -DPXR_BUILD_OPENIMAGEIO_PLUGIN=ON \
%endif
%if %{with openshading}
     -DPXR_ENABLE_OSL_SUPPORT=ON \
%endif
     -DPYTHON_EXECUTABLE=%{python3} \
%if %{with python3}
     -DPXR_USE_PYTHON_3=ON \
     -DPYSIDE_AVAILABLE=ON \
     -DPYSIDEUICBINARY:PATH=${PWD}/uic-wrapper \
%else
     -DPXR_ENABLE_PYTHON_SUPPORT=OFF \
%endif
     -DPXR_BUILD_MONOLITHIC=ON
%cmake_build

%install
%cmake_install

# Fix python3 files installation
mkdir -p %{buildroot}%{python3_sitearch}
mv %{buildroot}%{python3_sitelib}/* %{buildroot}%{python3_sitearch}

# Install a desktop icon for usdview
desktop-file-install                                    \
--dir=%{buildroot}%{_datadir}/applications              \
%{SOURCE1}
        
# Remove arch-specific code in /usr/share
find %{buildroot}%{_datadir}/%{name}/examples -name '*.so' -print -delete

# Fix installation path for some files
mv %{buildroot}%{_prefix}/lib/python/pxr/*.* \
        %{buildroot}%{python3_sitearch}/pxr/
mv %{buildroot}%{_prefix}/lib/python/pxr/Usdviewq/* \
        %{buildroot}%{python3_sitearch}/pxr/Usdviewq/
        
%check
desktop-file-validate %{buildroot}%{_datadir}/applications/org.open%{name}.%{name}view.desktop
%{?with_test:%ctest}

%files
%doc NOTICE.txt README.md
%{_bindir}/*
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/examples/
%{_datadir}/%{name}/examples/*

%if %{with python3}
%files -n python3-%{name}
%{_datadir}/applications/org.open%{name}.%{name}view.desktop
%{python3_sitearch}/pxr
%endif

%files libs
%license LICENSE.txt
%doc NOTICE.txt README.md
%{_libdir}/lib%{name}_ms.so.%{libmajor}
%{_libdir}/%{name}
%exclude %{_libdir}/%{name}/%{name}/resources/codegenTemplates

%files devel
%doc BUILDING.md CHANGELOG.md VERSIONS.md
%{_includedir}/pxr/
%{_libdir}/cmake/*
%{_libdir}/lib%{name}_ms.so
%{_libdir}/%{name}/%{name}/resources/codegenTemplates/

%if %{with documentation}
%files doc
%license LICENSE.txt
%{_docdir}/%{name}
%endif

%changelog
%autochangelog
