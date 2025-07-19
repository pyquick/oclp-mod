from oclp_mod import main
from oclp_mod import (
    constants,
    sucatalog
)
import json
import requests

KDK_API_LINK_PROXY:str  = "https://oclpapi.simplehac.cn/KdkSupportPkg/manifest.json"
KDK_API_LINK_ORIGIN:str  = "https://dortania.github.io/KdkSupportPkg/manifest.json"
KDK_API_LINK: str = KDK_API_LINK_ORIGIN
if __name__ == '__main__':
    #d={'ProductID': '082-42293', 'PostDate': datetime.datetime(2025, 5, 19, 17, 21, 30), 'Title': 'macOS Ventura', 'Build': '22H625', 'Version': '13.7.6', 'Catalog': '<SeedType.PublicRelease: ''>', 'InstallAssistant': {'URL': 'https://swcdn.apple.com/content/downloads/62/04/082-42293-A_BLBGWQXWM6/yxa6zwy8dit7wkvu39onjf7u60t235z0k0/InstallAssistant.pkg', 'Size': 12196639630, 'IntegrityDataURL': 'https://swcdn.apple.com/content/downloads/62/04/082-42293-A_BLBGWQXWM6/yxa6zwy8dit7wkvu39onjf7u60t235z0k0/InstallAssistant.pkg.integrityDataV1', 'IntegrityDataSize': 41972, 'XNUMajor': 22}}
    response = requests.get(KDK_API_LINK)
    response.raise_for_status()
    kdk_data = response.json()
    #kdk_data.pop("kernel_versions")
    print(json.dumps(kdk_data, indent=4))