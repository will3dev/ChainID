pragma solidity ^0.6.0;

contract WalletFactory {
    KYC_Wallet[] public deployedWallets;
    address public manager;
    uint public createWalletFee;
    uint public dataRequestFee;
    mapping(address => KYC_Wallet) public walletOwners;

    constructor (uint createFee, uint dataFee) public {
        manager = msg.sender;
        createWalletFee = createFee;
        dataRequestFee = dataFee;
    }

    function createWallet(string memory name, string memory home,
        string memory tin, string memory phone) public payable returns (KYC_Wallet) {
            require(msg.value >= createWalletFee, "Did not meet fee requirement");
            KYC_Wallet newWallet = new KYC_Wallet(msg.sender, manager, name, home, tin, phone, dataRequestFee);
            deployedWallets.push(newWallet);
            walletOwners[msg.sender] = newWallet;
            return newWallet;
        }

    function getDeployedWallets () public view returns (KYC_Wallet[] memory) {
        return deployedWallets;
    }
}

contract KYC_Wallet {
    struct Request {
        address requester;
        string name;
        string description;
        bool approved;
        bool active;
    }

    struct KYCData {
        string name;
        string home;
        string tin;
        string phone;
    }

    event WalletData(
        string name,
        string home,
        string tin,
        string phone
    );

    Request[] public requests;
    uint[] public request_ids;
    address public manager;
    address public owner;
    KYCData private data;
    uint public serviceCost;

    modifier restricted() {
        require(msg.sender == manager || msg.sender == owner);
        _;
    }

    constructor (address wallet_owner, address admin, string memory name, string memory home,
        string memory tin, string memory phone, uint serviceFee) public {
        manager = admin;
        owner = wallet_owner;
        data = KYCData({
            name: name,
            home:home,
            tin: tin,
            phone: phone
        });
        serviceCost = serviceFee;
    }

    function getData() public restricted view returns (string memory, string memory, string memory, string memory) {
        return (data.name, data.home, data.tin, data.phone);
    }

    function makeRequest(string memory name, string memory description) public payable returns (uint) {
        require(msg.value >= serviceCost, "Did not meet fee requirement.");

        Request memory newRequest = Request({
            requester: msg.sender,
            name: name,
            description: description,
            approved: false,
            active: true
        });
        requests.push(newRequest);
        uint val = request_ids.length;
        request_ids.push(val + 1);
        return val;
    }

    function approveRequest(uint index) public restricted {
        Request storage request = requests[index-1];

        request.approved = true;
    }

    function getKYCData(uint index) public {
        Request storage request = requests[index-1];

        require(request.approved == true, "Request not approved yet.");
        require(request.active == true, "Request is not active");
        require(msg.sender == request.requester, "Must be requested from request originator.");

        request.active = false;
        payable(manager).transfer(serviceCost/4);
        payable(owner).transfer((serviceCost/4)*3);
        emit WalletData(data.name, data.home, data.tin, data.phone);
    }

    function getRequests() public view returns (uint[] memory) {
        return request_ids;
    }
}
