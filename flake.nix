# code-owner: @agoose77
# This flake sets up a dev-shell that installs all the required
# packages for running deployer, and then installs the tool in the virtual environment
# It is not best-practice for the nix-way of distributing this code,
# but its purpose is to get an environment up and running.
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    dev-python = {
      url = "github:agoose77/dev-flakes/v10?dir=python";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  outputs = {
    self,
    nixpkgs,
    dev-python,
  }: let
    forAllSystems = nixpkgs.lib.genAttrs nixpkgs.lib.systems.flakeExposed;
  in {
    devShells = forAllSystems (system: let
      pkgs = import nixpkgs {
        inherit system;
      };

      # Define our interpreter
      python = pkgs.python314;

      # Configure the hook for enabling venvs
      # I think there's a way to auto-detect this, but
      # let's worry about that another time
      venvHook =
        dev-python.packages.${system}.nix-ld-venv-hook.override
        {python = python;};
      # Define our env packages (including the above)
      packages =
        [
          python
          venvHook
        ]
        ++ (with pkgs; [
          cmake
          ninja
          gcc
          pre-commit
        ]);
      # Unset these unwanted env vars
      # PYTHONPATH bleeds from Nix Python packages
      unwantedEnvPreamble = ''
        unset SOURCE_DATE_EPOCH PYTHONPATH
      '';
    in {
      default = pkgs.mkShell {
        inherit packages;
        # Define additional input for patching interpreter

        venvDir = ".venv";

        # Drop bad env vars on activation
        postShellHook = unwantedEnvPreamble;

        postVenvCreation =
          # Install pre-commit
          ''
            pre-commit install
          '';
      };
    });
  };
}
