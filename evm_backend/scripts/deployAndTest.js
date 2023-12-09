async function main() {
    const zeroSwipes = await hre.ethers.deployContract("ZeroSwipes");
  
    await zeroSwipes.waitForDeployment();
  
    console.log(
      `ZeroSwipes  deployed to ${zeroSwipes.target}`
    );

    // Interact with the contract
    const [owner, user1, user2, user3] = await hre.ethers.getSigners();

    // User1 and User2 go live
    await zeroSwipes.connect(user1).goLive(0, { value: hre.ethers.parseEther("1") });
    await zeroSwipes.connect(user2).goLive(1, { value: hre.ethers.parseEther("1") });

    // User3 recommends User2 to User1
    await zeroSwipes.connect(user3).recommend(user1.address, [user2.address]);

    // Fetch recommendations for User1
    const recommendations = await zeroSwipes.getRecommendations(user1.address);
    console.log("Recommendations for User1:", recommendations);

    // Match User1 and User2
    await zeroSwipes.connect(owner).matchAndDistributeBounty(user1.address, user2.address);
    console.log("Matched User1 and User2");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });