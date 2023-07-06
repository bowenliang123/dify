import React, { useEffect, useState } from 'react'
import classNames from 'classnames'
import style from './workspace.module.css'
import Button from '@/app/components/base/button'
import Dialog from '@/app/components/base/dialog'
import { getUsers } from '@/service/workspace'

type CheckedDialogProps = {
  show: boolean
  dataList: object
  onClose?: () => void
}

const CheckedDialog = ({ show, dataList, onClose }: CheckedDialogProps) => {
  const [checkedList, setCheckedList] = useState([])

  const getUsersList = async (params: { tenant_id: string }) => {
    const ans: any = await getUsers(params)
    if (ans.result === 'success')
      setCheckedList(ans.data)
    else
      setCheckedList([])
  }

  useEffect(() => {
    if (dataList.id)
      getUsersList({ tenant_id: dataList.id })
  }, [dataList])

  const onClosed = () => {
    if (onClose)
      onClose()
  }

  return (
    <div>
      <Dialog
        show={show}
        title='查看关联用户'
        footer={
          <>
            <Button onClick={onClosed}>关闭</Button>
          </>
        }
      >
        <div className={classNames(style.connectedStyle)}>
          <div className={style.connectedtableStyle}>
            {/* 已关联的用户列表 */}
            <table style={{ width: 1700 }}>
              <thead className="h-12 leading-8 border-b  border-gray-200 text-gray-500 font-bold">
                <tr>
                  <td>用户</td>
                  <td>邮箱</td>
                  <td>语言</td>
                  <td>时区</td>
                  <td>最后登录</td>
                  <td>最后登录ip</td>
                  <td>创建</td>
                  <td>角色</td>
                </tr>
              </thead>
              <tbody>
                {checkedList.map((item: any) => {
                  return (
                    <tr
                      className={'border-b border-gray-200 h-12 hover:bg-gray-50 cursor-pointer'}
                    >
                      <td>{item.name}</td>
                      <td>{item.email}</td>
                      <td>{item.interface_language}</td>
                      <td>{item.timezone}</td>
                      <td>{item.last_login_at}</td>
                      <td>{item.last_login_ip}</td>
                      <td>{item.created_at}</td>
                      <td>{item.role}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      </Dialog>
    </div>
  )
}

export default CheckedDialog
