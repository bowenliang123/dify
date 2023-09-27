import React, { useState } from 'react'
import { useContext } from 'use-context-selector'
import style from './workspace.module.css'
import Button from '@/app/components/base/button'
import Dialog from '@/app/components/base/dialog'
import { ToastContext } from '@/app/components/base/toast'
import { connectUsers, getListbyname } from '@/service/workspace'

type ConnectedDialogProps = {
  show: boolean
  dataList: object
  onClose?: () => void
  onSuccess?: () => void
}

const ConnectedDialog = ({ show, dataList, onClose, onSuccess }: ConnectedDialogProps) => {
  const { notify } = useContext(ToastContext)

  const [connectedList, setconnectedList] = useState([])
  const [selectList, setSelectList] = useState([])
  const [showConfirm, setShowConfirm] = useState(false)

  const onClosed = () => {
    if (onClose) {
      onClose()
      setconnectedList([])
    }
  }

  const onCreated = () => {
    const lists: any = []
    const roleEle = document.getElementsByClassName('roleVale')
    document.getElementsByName('checkbox').forEach((element) => {
      if (element.checked) {
        const dataVal = JSON.parse(element.value)
        if (roleEle[0]?.value?.length > 0)
          dataVal.role = roleEle[0].value

        lists.push(dataVal)
      }
    })
    if (lists.length <= 0) {
      notify({ type: 'info', message: '请至少选中一个用户' })
      return false
    }
    setSelectList(lists)
    setShowConfirm(true)
  }

  const onSearch = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.currentTarget.blur()
      const ans: any = await getListbyname({ name: e.target.value })
      if (ans.length > 0)
        setconnectedList(ans)
      else
        setconnectedList([])
    }
  }

  const onConnected = () => {
    const params = selectList.map((item) => {
      return { user_id: item.id, tenant_id: dataList.id, role: item.role }
    })
    let resArr = true
    params.forEach(async (it) => {
      const ans: any = await connectUsers(it)
      if (ans.result !== 'success')
        resArr = false
    })
    if (resArr) {
      notify({ type: 'success', message: '添加成功' })
      setShowConfirm(false)
      if (onSuccess) {
        onSuccess()
        setconnectedList([])
      }
    }
  }

  return (
    <div>
      <Dialog
        show={show}
        title='关联用户'
        footer={
          <>
            <Button onClick={onClosed}>取消</Button>
            <Button type="primary" onClick={onCreated}>创建</Button>
          </>
        }
      >
        <div style={{ display: 'inline-block' }}>
          用户姓名：
          <input type="text" onKeyDown={(e) => { onSearch(e) }} className='h-10 px-3 text-sm font-normal bg-gray-100 rounded-lg grow' />
        </div>
        <div style={{ display: 'inline-block', marginLeft: 30 }}>
          角色：
          <select className='roleVale' style={{ width: 180, borderRadius: 8, height: 40, backgroundColor: '#F3F4F6' }}>
            <option value="">请选择角色</option>
            <option value="admin">admin</option>
            <option value="owner">owner</option>
            <option value="normal">normal</option>
          </select>
        </div>
        <div className={connectedList.length > 0 ? style.connectedtableStyle : ''}>
          {connectedList.length > 0
            ? <table style={{ width: 1700 }}>
              <thead className="h-12 leading-8 border-b  border-gray-200 text-gray-500 font-bold">
                <tr>
                  <td></td>
                  <td>用户</td>
                  <td>邮箱</td>
                  <td>语言</td>
                  <td>时区</td>
                  <td>最后登录</td>
                  <td>最后登录ip</td>
                  <td>创建</td>
                </tr>
              </thead>
              <tbody>
                {connectedList.map((item: any) => {
                  return (
                    <tr
                      className={'border-b border-gray-200 h-12 hover:bg-gray-50 cursor-pointer'}
                    >
                      <td>
                        <input type="checkbox" value={JSON.stringify(item)} name='checkbox' />
                      </td>
                      <td>{item.name}</td>
                      <td>{item.email}</td>
                      <td>{item.interface_language}</td>
                      <td>{item.timezone}</td>
                      <td>{item.last_login_at}</td>
                      <td>{item.last_login_ip}</td>
                      <td>{item.created_at}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
            : ''
          }
        </div>
      </Dialog>
      <Dialog
        show={showConfirm}
        title='提示'
        footer={
          <>
            <Button onClick={() => { setShowConfirm(false) }}>取消</Button>
            <Button type="primary" onClick={onConnected}>确定</Button>
          </>
        }
      >
        <div>是否将该用户加入空间？</div>
      </Dialog>
    </div>
  )
}

export default ConnectedDialog
