"""
依赖安全检查模块 - Dependency security check module.

解析requirements.txt和package.json，检查已知漏洞包。
Parses requirements.txt and package.json, checks for known vulnerable packages.

使用内置漏洞数据库进行检查，不依赖外部服务。
Uses a built-in vulnerability database for checking, no external services needed.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# 内置已知漏洞数据库
# 数据格式: {包名: [{"id": "CVE-xxxx-xxxx", "affected_versions": "范围", "severity": "高/中/低", "description": "描述"}]}
# 注意：此为演示用的小型数据库，实际使用时应定期更新
VULNERABILITY_DB: Dict[str, List[Dict[str, str]]] = {
    "requests": [
        {
            "id": "CVE-2023-32681",
            "affected_versions": "<2.31.0",
            "severity": "medium",
            "description": "requests库在处理多部分表单数据时存在信息泄露风险",
        },
    ],
    "urllib3": [
        {
            "id": "CVE-2023-45803",
            "affected_versions": "<2.0.7",
            "severity": "medium",
            "description": "urllib3请求注入漏洞，允许绕过请求头限制",
        },
    ],
    "flask": [
        {
            "id": "CVE-2023-30861",
            "affected_versions": "<2.3.2",
            "severity": "high",
            "description": "Flask异常处理中的XSS漏洞",
        },
    ],
    "django": [
        {
            "id": "CVE-2023-46695",
            "affected_versions": "<4.2.7",
            "severity": "high",
            "description": "Django潜在SQL注入漏洞",
        },
        {
            "id": "CVE-2023-41164",
            "affected_versions": "<4.2.5",
            "severity": "medium",
            "description": "Django DoS漏洞",
        },
    ],
    "pillow": [
        {
            "id": "CVE-2023-44271",
            "affected_versions": "<10.0.1",
            "severity": "high",
            "description": "Pillow缓冲区溢出漏洞",
        },
    ],
    "pyyaml": [
        {
            "id": "CVE-2020-14343",
            "affected_versions": "<5.4",
            "severity": "high",
            "description": "PyYAML在加载不受信任的YAML时存在任意代码执行漏洞",
        },
    ],
    "numpy": [
        {
            "id": "CVE-2021-33430",
            "affected_versions": "<1.21.1",
            "severity": "medium",
            "description": "NumPy缓冲区溢出漏洞",
        },
    ],
    "lodash": [
        {
            "id": "CVE-2021-23337",
            "affected_versions": "<4.17.21",
            "severity": "high",
            "description": "Lodash命令注入漏洞",
        },
    ],
    "express": [
        {
            "id": "CVE-2024-29041",
            "affected_versions": "<4.19.2",
            "severity": "high",
            "description": "Express开放重定向漏洞",
        },
    ],
    "axios": [
        {
            "id": "CVE-2023-45857",
            "affected_versions": "<1.6.0",
            "severity": "medium",
            "description": "Axios CSRF漏洞",
        },
    ],
    "minimist": [
        {
            "id": "CVE-2020-7598",
            "affected_versions": "<1.2.6",
            "severity": "high",
            "description": "minimist原型污染漏洞",
        },
    ],
    "jsonwebtoken": [
        {
            "id": "CVE-2022-23529",
            "affected_versions": "<9.0.0",
            "severity": "high",
            "description": "jsonwebtoken存在远程代码执行漏洞",
        },
    ],
    "log4js": [
        {
            "id": "CVE-2022-31114",
            "affected_versions": "<6.7.1",
            "severity": "medium",
            "description": "log4js存在任意文件写入漏洞",
        },
    ],
}


class DependencyChecker:
    """依赖安全检查器。

    Dependency security checker that parses dependency files
    and checks packages against a built-in vulnerability database.
    """

    def __init__(self) -> None:
        """初始化依赖检查器。"""
        self._vuln_db = VULNERABILITY_DB

    def parse_requirements_txt(self, filepath: str) -> List[Dict[str, str]]:
        """解析requirements.txt文件。

        Parse a requirements.txt file.

        支持的格式：
        - package==1.0.0
        - package>=1.0.0
        - package~=1.0.0
        - package!=1.0.0
        - package  (无版本约束)
        - # 注释行
        - -r other_file.txt  (忽略)
        - --index-url ...  (忽略)

        Args:
            filepath: requirements.txt文件路径. Path to requirements.txt.

        Returns:
            依赖包列表，每项包含name和version_spec。
            List of dependency dicts with name and version_spec.
        """
        deps = []
        path = Path(filepath)

        if not path.exists():
            return deps

        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except OSError:
            return deps

        for line in lines:
            line = line.strip()

            # 跳过空行、注释和选项
            if not line or line.startswith("#") or line.startswith("-"):
                continue

            # 解析包名和版本
            dep = self._parse_pip_requirement(line)
            if dep:
                deps.append(dep)

        return deps

    def parse_package_json(self, filepath: str) -> List[Dict[str, str]]:
        """解析package.json文件。

        Parse a package.json file.

        Args:
            filepath: package.json文件路径. Path to package.json.

        Returns:
            依赖包列表，每项包含name和version。
            List of dependency dicts with name and version.
        """
        deps = []
        path = Path(filepath)

        if not path.exists():
            return deps

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return deps

        # 解析dependencies和devDependencies
        for section in ("dependencies", "devDependencies"):
            section_deps = data.get(section, {})
            if isinstance(section_deps, dict):
                for name, version in section_deps.items():
                    deps.append({
                        "name": name,
                        "version_spec": version,
                        "section": section,
                    })

        return deps

    def check_dependencies(
        self,
        deps: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """检查依赖包是否存在已知漏洞。

        Check dependencies for known vulnerabilities.

        Args:
            deps: 依赖包列表. List of dependency dicts.

        Returns:
            漏洞报告列表. List of vulnerability report dicts.
        """
        vulnerabilities = []

        for dep in deps:
            name = dep.get("name", "").lower()
            version_spec = dep.get("version_spec", "")

            # 在漏洞数据库中查找
            vulns = self._vuln_db.get(name, [])

            for vuln in vulns:
                # 提取当前安装的版本
                installed_version = self._extract_version(version_spec)

                # 检查是否受影响
                if installed_version and self._is_affected(
                    installed_version, vuln["affected_versions"]
                ):
                    vulnerabilities.append({
                        "package": name,
                        "installed_version": installed_version,
                        "vulnerability_id": vuln["id"],
                        "severity": vuln["severity"],
                        "description": vuln["description"],
                        "affected_versions": vuln["affected_versions"],
                        "fix": f"升级到不受影响的版本",
                    })

        return vulnerabilities

    def check_file(self, filepath: str) -> Dict[str, Any]:
        """检查单个依赖文件。

        Check a single dependency file.

        Args:
            filepath: 依赖文件路径. Path to dependency file.

        Returns:
            检查结果字典. Check result dict.
        """
        path = Path(filepath)
        filename = path.name.lower()

        if filename == "requirements.txt" or filename.endswith(".txt"):
            deps = self.parse_requirements_txt(filepath)
            file_type = "pip"
        elif filename == "package.json" or filename.endswith(".json"):
            deps = self.parse_package_json(filepath)
            file_type = "npm"
        else:
            return {
                "file": filepath,
                "error": "不支持的文件类型",
                "dependencies": [],
                "vulnerabilities": [],
                "summary": {},
            }

        vulns = self.check_dependencies(deps)

        # 统计摘要
        severity_counts: Dict[str, int] = {"high": 0, "medium": 0, "low": 0}
        for v in vulns:
            sev = v.get("severity", "low").lower()
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        return {
            "file": filepath,
            "file_type": file_type,
            "total_dependencies": len(deps),
            "dependencies": deps,
            "vulnerabilities": vulns,
            "summary": {
                "total_vulnerabilities": len(vulns),
                "high": severity_counts["high"],
                "medium": severity_counts["medium"],
                "low": severity_counts["low"],
                "safe": len(deps) - len(set(v["package"] for v in vulns)),
            },
        }

    @staticmethod
    def _parse_pip_requirement(line: str) -> Optional[Dict[str, str]]:
        """解析pip依赖行。

        Parse a pip requirement line.

        Args:
            line: 依赖行. Requirement line.

        Returns:
            依赖字典或None. Dependency dict or None.
        """
        # 匹配: package==1.0.0, package>=1.0.0, package~=1.0.0, package!=1.0.0
        match = re.match(
            r"^([a-zA-Z0-9][a-zA-Z0-9._-]*)\s*(==|>=|<=|~=|!=|>|<)?\s*(.*)?$",
            line,
        )
        if match:
            name = match.group(1).lower()
            operator = match.group(2) or ""
            version = match.group(3) or ""
            version_spec = f"{operator}{version}" if operator else version
            return {"name": name, "version_spec": version_spec}
        return None

    @staticmethod
    def _extract_version(version_spec: str) -> str:
        """从版本规格中提取版本号。

        Extract version number from version specification.

        Args:
            version_spec: 版本规格字符串. Version spec string.

        Returns:
            版本号字符串. Version number string.
        """
        # 移除常见前缀: ^, ~, >=, <=, ==, !=, >, <, v
        cleaned = re.sub(r"^[^0-9]*", "", version_spec.strip())
        # 取第一个版本号（可能包含预发布标识）
        match = re.match(r"^(\d+\.\d+\.\d+)", cleaned)
        if match:
            return match.group(1)
        return cleaned

    @staticmethod
    def _is_affected(version: str, affected_range: str) -> bool:
        """检查版本是否在受影响范围内。

        Check if a version falls within the affected range.

        Args:
            version: 要检查的版本. Version to check.
            affected_range: 受影响版本范围 (如 "<2.31.0").
                           Affected version range (e.g., "<2.31.0").

        Returns:
            是否受影响. Whether affected.
        """
        try:
            # 解析版本号
            v_parts = [int(x) for x in version.split(".")[:3]]
            # 补齐到3位
            while len(v_parts) < 3:
                v_parts.append(0)

            # 解析受影响范围
            if affected_range.startswith("<"):
                target = affected_range[1:].strip()
                t_parts = [int(x) for x in target.split(".")[:3]]
                while len(t_parts) < 3:
                    t_parts.append(0)
                return v_parts < t_parts

            elif affected_range.startswith("<="):
                target = affected_range[2:].strip()
                t_parts = [int(x) for x in target.split(".")[:3]]
                while len(t_parts) < 3:
                    t_parts.append(0)
                return v_parts <= t_parts

            elif affected_range.startswith(">="):
                target = affected_range[2:].strip()
                t_parts = [int(x) for x in target.split(".")[:3]]
                while len(t_parts) < 3:
                    t_parts.append(0)
                return v_parts >= t_parts

            elif affected_range.startswith(">"):
                target = affected_range[1:].strip()
                t_parts = [int(x) for x in target.split(".")[:3]]
                while len(t_parts) < 3:
                    t_parts.append(0)
                return v_parts > t_parts

            elif affected_range.startswith("=="):
                target = affected_range[2:].strip()
                t_parts = [int(x) for x in target.split(".")[:3]]
                while len(t_parts) < 3:
                    t_parts.append(0)
                return v_parts == t_parts

            # 不支持的格式，默认不受影响
            return False

        except (ValueError, IndexError):
            return False

    def get_vulnerability_db_info(self) -> Dict[str, Any]:
        """获取漏洞数据库信息。

        Get vulnerability database information.

        Returns:
            数据库信息字典. Database info dict.
        """
        total_packages = len(self._vuln_db)
        total_vulns = sum(len(v) for v in self._vuln_db.values())
        severity_counts: Dict[str, int] = {"high": 0, "medium": 0, "low": 0}

        for vulns in self._vuln_db.values():
            for v in vulns:
                sev = v.get("severity", "low").lower()
                severity_counts[sev] = severity_counts.get(sev, 0) + 1

        return {
            "total_packages_tracked": total_packages,
            "total_vulnerabilities": total_vulns,
            "severity_distribution": severity_counts,
            "packages": list(self._vuln_db.keys()),
        }
