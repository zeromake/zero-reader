const requireAll = function(requireContext) {
    return requireContext.keys().map(requireContext)
}
const req = require.context('.', false, /\.svg$/)
requireAll(req)
export default ""
