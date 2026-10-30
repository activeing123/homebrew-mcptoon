class Mcptoon < Formula
  include Language::Python::Virtualenv

  desc "MCP client and token-efficient tool manifest layer for AI agents"
  homepage "https://github.com/activeing123/mcptoon"
  url "https://github.com/activeing123/mcptoon/archive/refs/tags/v0.8.34.tar.gz"
  sha256 "feace2f236a7bc9a85300868fe3eb562a29f50ecb449b0b80af1f1dcedb72865"
  license "Apache-2.0"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/mcptoon --version")
  end
end
