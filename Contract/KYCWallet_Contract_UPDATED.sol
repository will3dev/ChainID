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

    function getFactoryData () public view returns (uint, uint, address) {
        return (createWalletFee, dataRequestFee, manager);
    }

    function updateRequestFee(uint amount) public {
        require(msg.sender == manager, "Only manager can update fee");
        dataRequestFee = amount;
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

    mapping(address => Request) public requests;
    address[] public request_ids;
    address[] public approved_requests;
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

    function makeRequest(string memory name, string memory description) public payable {
        require(msg.value >= serviceCost, "Did not meet fee requirement.");
        Request memory r = requests[msg.sender];
        require(r.approved || (!r.approved && r.requester == 0x0000000000000000000000000000000000000000), "There is an active request.");

        Request memory newRequest = Request({
            requester: msg.sender,
            name: name,
            description: description,
            approved: false,
            active: true
        });
        requests[msg.sender] = newRequest;
        address sender = msg.sender;
        request_ids.push(sender);
    }

    function approveRequest(address requester) public restricted {

        for (uint i = 0; i < request_ids.length; i++) {
            if (request_ids[i] == requester) {
                address last_val = request_ids[request_ids.length - 1];
                request_ids[i] = last_val;
                request_ids.pop();
                approved_requests.push(requester);

                Request storage request = requests[requester];
                request.approved = true;

                payable(manager).transfer(serviceCost/4);
                payable(owner).transfer((serviceCost/4)*3);
            }
        }


    }

    function getKYCData() public {
        Request storage request = requests[msg.sender];

        require(request.approved == true, "Request not approved yet.");
        require(request.active == true, "Data has already been gathered.");
        require(msg.sender == request.requester, "Must be requested from request originator.");

        request.active = false;

        emit WalletData(data.name, data.home, data.tin, data.phone);
    }

    function getRequests() public view returns (address[] memory) {
        return request_ids;
    }

    function getApprovedRequests() public view returns (address[] memory) {
        return approved_requests;
    }

    function getWalletDetails()  public view returns (address, address, uint, uint, uint) {
        return (manager, owner, serviceCost, request_ids.length, approved_requests.length);
    }
}