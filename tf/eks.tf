# provider "kubernetes" {
#   host                   = data.aws_eks_cluster.auth_cluster.endpoint
#   cluster_ca_certificate = base64decode(aws_eks_cluster.auth_cluster.certificate_authority[0].data)
#   token                  = data.aws_eks_cluster_auth.auth_cluster.token
# }

# data "aws_eks_cluster" "auth_cluster" {
#   name = local.cluster_name
# }

# data "aws_eks_cluster_auth" "auth_cluster" {
#   name = data.aws_eks_cluster.auth_cluster.name
# }