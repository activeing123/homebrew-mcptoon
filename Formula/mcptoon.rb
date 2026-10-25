class Mcptoon < Formula
  include Language::Python::Virtualenv

  desc "MCP client and token-efficient tool manifest layer for AI agents"
  homepage "https://github.com/activeing123/mcptoon"
  url "https://github.com/activeing123/mcptoon/archive/refs/tags/v0.8.28.tar.gz"
  sha256 "2326cf850e52c0b470ab94480c9b5d300418fdcfea7cf75e1d604e73c8635b6b"
  license "Apache-2.0"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/mcptoon --version")
  end
end
