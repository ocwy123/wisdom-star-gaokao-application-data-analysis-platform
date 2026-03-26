// 中文字体加载脚本
// 这个脚本会加载中文字体用于 PDF 导出

// 使用 base64 编码的思源黑体字体（简化版，仅包含常用汉字）
// 在实际项目中，应该加载完整的字体文件
const loadChineseFont = async () => {
  // 尝试从 CDN 加载字体
  const fontUrl = 'https://cdn.jsdelivr.net/npm/simhei@1.0.0/simhei.ttf'
  
  try {
    const response = await fetch(fontUrl)
    if (!response.ok) {
      throw new Error('Failed to load font')
    }
    const fontBuffer = await response.arrayBuffer()
    return fontBuffer
  } catch (error) {
    console.warn('无法从 CDN 加载字体，使用备用方案')
    // 备用方案：返回 null，PDF 将使用默认字体
    return null
  }
}

export { loadChineseFont }
