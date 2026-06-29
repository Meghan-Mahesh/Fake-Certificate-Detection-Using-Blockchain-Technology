// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract CertificateStorage {

    struct Certificate {
        bytes32 certHash;
        string issuerId;
        uint256 issuedAt;
        bool exists;
    }

    mapping(string => Certificate) private certificates;

    event CertificateStored(
        string certId,
        bytes32 certHash,
        string issuerId,
        uint256 timestamp
    );

    // 🔥 STORE CERTIFICATE
    function storeCertificateHash(
        string memory certId,
        bytes32 certHash,
        string memory issuerId
    ) public {

        require(!certificates[certId].exists, "Certificate already exists");

        certificates[certId] = Certificate({
            certHash: certHash,
            issuerId: issuerId,
            issuedAt: block.timestamp,
            exists: true
        });

        emit CertificateStored(certId, certHash, issuerId, block.timestamp);
    }

    // 🔍 FETCH CERTIFICATE DETAILS
    function getCertificateDetails(string memory certId)
        public view returns (
            bytes32 certHash,
            string memory issuerId,
            uint256 issuedAt
        )
    {
        require(certificates[certId].exists, "Certificate not found");

        Certificate memory cert = certificates[certId];
        return (cert.certHash, cert.issuerId, cert.issuedAt);
    }

    // 🔍 CHECK IF EXISTS
    function certificateExists(string memory certId)
        public view returns (bool)
    {
        return certificates[certId].exists;
    }
}