import { Button, Checkbox, Input, Space } from 'ant-design-vue'
import { h, reactive, ref } from 'vue'
import { SEARCH_DEBOUNCE_MS } from '@/utils/const.js'

/**
 * 表格表头「多选 + 搜索」筛选通用逻辑
 * @param { (columnKey: string, search: string) => Promise<Array<{ label: string, value: any }>> } loadOptions - 按列和搜索词拉取选项，返回 { label, value }[]
 * @returns { filterOptionsCache, filterSearchState, loadFilterOptions, renderMultiSelectFilterDropdown }
 */
export function useTableMultiSelectFilter(loadOptions) {
  const filterOptionsCache = reactive({})
  const filterSearchState = reactive({})
  const filterSearchTimers = ref({})

  async function loadFilterOptions(columnKey, search = '') {
    try {
      const options = await loadOptions(columnKey, search)
      filterOptionsCache[columnKey] = options || []
    } catch (e) {
      console.error(e)
      filterOptionsCache[columnKey] = []
    }
  }

  /**
   * 用于 a-table column 的 filterDropdown，带搜索框 + 多选 + 清除/确定
   * @param { { columnKey: string, placeholder?: string } } opts
   */
  function renderMultiSelectFilterDropdown({ columnKey, placeholder = '' }) {
    return ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => {
      const checkedValues = selectedKeys || []
      const searchValue = filterSearchState[columnKey] ?? ''
      const options = filterOptionsCache[columnKey] || []

      const handleSearchChange = (val) => {
        filterSearchState[columnKey] = val ?? ''
        const timers = filterSearchTimers.value
        if (timers[columnKey]) clearTimeout(timers[columnKey])
        timers[columnKey] = setTimeout(() => {
          loadFilterOptions(columnKey, val ?? '')
        }, SEARCH_DEBOUNCE_MS)
      }

      const handleCheckChange = (checkedList) => {
        setSelectedKeys(checkedList)
      }

      return h(
        'div',
        {
          class: 'table-multi-select-filter-dropdown',
          style: { padding: '8px', minWidth: '200px' },
        },
        [
          h(Input, {
            value: searchValue,
            placeholder: placeholder ? `搜索${placeholder}` : '搜索',
            style: { width: '100%', marginBottom: '8px' },
            allowClear: true,
            'onUpdate:value': handleSearchChange,
          }),
          h(
            'div',
            { style: { maxHeight: '200px', overflowY: 'auto', marginBottom: '8px' } },
            options.length
              ? h(
                  Checkbox.Group,
                  {
                    value: checkedValues,
                    'onUpdate:value': handleCheckChange,
                    style: { display: 'flex', flexDirection: 'column', gap: '4px' },
                  },
                  () =>
                    options.map((opt) =>
                      h(Checkbox, { value: opt.value, key: String(opt.value) }, () => opt.label),
                    ),
                )
              : h('div', { style: { padding: '8px', color: '#999' } }, '无匹配项'),
          ),
          h(Space, { style: { justifyContent: 'flex-end', width: '100%' } }, [
            h(
              Button,
              { size: 'small', onClick: () => clearFilters && clearFilters() },
              () => '清除',
            ),
            h(Button, { type: 'primary', size: 'small', onClick: () => confirm() }, () => '确定'),
          ]),
        ],
      )
    }
  }

  return {
    filterOptionsCache,
    filterSearchState,
    loadFilterOptions,
    renderMultiSelectFilterDropdown,
  }
}
