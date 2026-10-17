class Mcptoon < Formula
  include Language::Python::Virtualenv

  desc "MCP client and token-efficient tool manifest layer for AI agents"
  homepage "https://github.com/activeing123/mcptoon"
  url "https://github.com/activeing123/mcptoon/archive/refs/tags/v0.8.22.tar.gz"
  sha256 "e633fcd704f3a42392d95a6d21570db62732ed1e2ac0117b04383a98ea567e4a"
  license "Apache-2.0"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/mcptoon --version")
  end
end
