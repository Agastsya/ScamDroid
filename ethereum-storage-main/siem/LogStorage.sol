// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LogStorage {
    string[] public logs;

    function storeLog(string memory log) public {
        logs.push(log);
    }

    function getLogs() public view returns (string[] memory) {
        return logs;
    }
}
