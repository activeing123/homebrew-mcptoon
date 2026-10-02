class Mcptoon < Formula
  include Language::Python::Virtualenv

  desc "MCP client and token-efficient tool manifest layer for AI agents"
  homepage "https://github.com/activeing123/mcptoon"
  url "https://github.com/activeing123/mcptoon/archive/refs/tags/v0.8.10.tar.gz"
  sha256 "96ac3af4e665bcba257cc5d5e40859e5e8c27eed92e815503b3e50f4405c0820"
  license "Apache-2.0"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/mcptoon --version")
  end
end
