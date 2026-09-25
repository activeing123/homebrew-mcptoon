class Mcptoon < Formula
  include Language::Python::Virtualenv

  desc "MCP client and token-efficient tool manifest layer for AI agents"
  homepage "https://github.com/activeing123/mcptoon"
  url "https://github.com/activeing123/mcptoon/archive/refs/tags/v0.8.1.tar.gz"
  sha256 "06d7518fc036cc7f83db9fea4ac49c275f5c011b8ec7ca5d9c8aa52b5cea3085"
  license "Apache-2.0"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/mcptoon --version")
  end
end
