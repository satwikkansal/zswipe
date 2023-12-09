require("@nomicfoundation/hardhat-toolbox");
require('dotenv').config()


/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.19",
  networks: {
    hardhat: {
      forking: {
        url: "https://scroll-sepolia.blockpi.network/v1/rpc/public",
      },
    },
    sepolia: {
      url: "https://scroll-sepolia.blockpi.network/v1/rpc/public",
      chainId: 534351,
      // Add other network configuration here like accounts
      // private key
      accounts: [process.env.PRIVATE_KEY_1],
    },
  },
};
