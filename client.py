import grpc
import proof_pb2
import proof_pb2_grpc
import numpy as np
import sympy
import parameters

def register_with_server():
    # Get parameters g, h, q
    # g and h generate groups G and H of prime order q
    #parameters_request = proof_pb2.ParametersRequest()
    #parameters_response = stub.Parameters(parameters_request)

    # Check if parameters were received
    #if parameters_response.g and parameters_response.h and parameters_response.q:
    print(f"Parameters: q: {parameters.p} g: {parameters.g}, h: {parameters.h}")

    # Choose numerical password x
    # x = abs(int(input("Enter numerical password x: "))) % parameters.p
    x = sympy.Mod(abs(sympy.Integer(input("Enter numerical password x: "))), parameters.p)
        
    # Generate y1 = g^x and y2 = h^x
    #y1 =(parameters.g**x) % parameters.q
    #y2 = (parameters.h**x) % parameters.q
    y1 = sympy.Mod(sympy.Pow(parameters.g, x), parameters.p)
    y2 = sympy.Mod(sympy.Pow(parameters.h, x), parameters.p)

    # Send y1 and y2 as registration
    registration_request = proof_pb2.RegistrationRequest(y1=str(y1), y2=str(y2))
    registration_response = stub.Register(registration_request)

    if registration_response:
        # Print y1 and y2 for client's reference
        print(f"Successful registration. y1: {y1}. y2: {y2}")
        #return parameters.g, parameters.h, parameters.p, x
        return

    else:
        print("Server has not produced values for g, h and q") 
        return

#def login_to_server(g, h, q):
def login_to_server():
    # Create a gRPC channel and stub
    channel = grpc.insecure_channel('localhost:50051')
    stub = proof_pb2_grpc.ChaumPedersenServiceStub(channel)

    print('Starting login')

    # Choose numerical password x
    #x = abs(int(input("Enter numerical password x: "))) % parameters.p
    x = sympy.Mod(abs(sympy.Integer(input("Enter numerical password x: "))), parameters.p)

    # Generate commitment values
    k = sympy.Integer(np.random.randint(1, high=np.iinfo(np.int32).max, dtype=np.int32) % parameters.p)
    #k = np.random.randint(1, high=2**128, dtype=np.int32) % q
    # r1 = g^k and r2 = h^k
    #r1 = (parameters.g**k) % parameters.p
    #r2 = (parameters.h**k) % parameters.p
    r1 = sympy.Mod(sympy.Pow(parameters.g, k), parameters.p)
    r2 = sympy.Mod(sympy.Pow(parameters.h, k), parameters.p)
    
    # Send commitment to server
    commitment_request = proof_pb2.CommitmentChallengeRequest(r1=str(r1), r2=str(r2))
    print(f"Commitment sent. r1: {r1}. r2: {r2}")

    commitment_response = stub.CommitmentChallenge(commitment_request)
    print(f"Challenge received. c: {commitment_response.c}")

    # Generate zkp
    s = sympy.Mod(k - sympy.Mul(sympy.Integer(commitment_response.c), x), parameters.p)
    print(f"Proof sent. s = {str(s)}")
    
    # Send proof to server
    proof_request = proof_pb2.VerifyProofRequest(s=str(s))
    proof_response = stub.VerifyProof(proof_request)
    if proof_response.success:
        print('Successful login. Proof accepted by server.')
        return
    else:
        print('Login failed')
        return


if __name__ == '__main__':
    # Create a gRPC channel and stub
    channel = grpc.insecure_channel('localhost:50051')
    stub = proof_pb2_grpc.ChaumPedersenServiceStub(channel)

    # Register with the server
    #g, h, q, x = register_with_server()
    
    register_with_server()
    # Close communication with server
    # channel.close()

    # Create a gRPC channel and stub
    # channel = grpc.insecure_channel('localhost:50051')
    # stub = proof_pb2_grpc.ChaumPedersenServiceStub(channel)

    # Login to the server
    login_to_server()

    # Close communication with server
    channel.close()
