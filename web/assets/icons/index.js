var requireAll = function(requireContext) {
    return requireContext.keys().map(requireContext)
}
var req = require.context('.', false, /\.svg$/)
requireAll(req)
