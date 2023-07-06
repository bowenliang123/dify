'use client'
import React, { useEffect, useState } from 'react'
import { useContext } from 'use-context-selector'
import classNames from 'classnames'
import { ArrowLeftIcon, ArrowRightIcon } from '@heroicons/react/24/outline'
import { Pagination } from 'react-headless-pagination'
import { useTranslation } from 'react-i18next'
import style from './workspace.module.css'
import AddWorkspaceDialog from './AddWorkspaceDialog'
import CheckedDialog from './CheckedDialog'
import ConnectedDialog from './ConnectedDialog'
import { ToastContext } from '@/app/components/base/toast'
import { getAll } from '@/service/workspace'

const Workspace = () => {
  const { notify } = useContext(ToastContext)
  const { t } = useTranslation()

  const [workspaceList, setWorkspaceList] = useState([])
  const [currPage, setCurrPage] = useState(0)
  const [total, setTotal] = useState(0)
  const [limit, setLimit] = useState(10)
  const [showAddWorkspaceDialog, setShowAddWorkspaceDialog] = useState(false)
  const [showCheckedDialog, setShowCheckedDialog] = useState(false)
  const [showConnectedDialog, setShowConnectedDialog] = useState(false)
  const [checkedList, setCheckedList] = useState({})
  const [connectedList, setConnectedList] = useState({})

  const getAlls = async (params: { page: number; limit: number }) => {
    const { data, limit, total }: any = await getAll(params)

    setWorkspaceList(data)
    setLimit(limit)
    setTotal(total)
  }

  useEffect(() => {
    getAlls({ page: currPage + 1, limit })
  }, [currPage])

  const onCreate = async () => {
    setShowAddWorkspaceDialog(true)
  }

  const onSuccess = () => {
    setShowAddWorkspaceDialog(false)
    notify({ type: 'success', message: '新增workspace成功!' })
    setCurrPage(0)
  }

  const onChecked = (data: object) => {
    setCheckedList(data)
    setShowCheckedDialog(true)
  }

  const onConnected = (data: object) => {
    setConnectedList(data)
    setShowConnectedDialog(true)
  }

  const onConnectedSuc = () => {
    setShowConnectedDialog(false)
    if (currPage === 0)
      getAlls({ page: 1, limit })
    else
      setCurrPage(0)
  }

  return (
    <div className={classNames(style.workspaceStyle, 'border-t')}>
      <div className={style.createBtn}>
        <button type="button" onClick={() => onCreate()}>新增workspace</button>
      </div>
      <div className={style.tableStyle}>
        {/* 表格 */}
        <table>
          <thead className="h-12 leading-8 border-b  border-gray-200 text-gray-500 font-bold">
            <tr>
              <td>空间名称</td>
              <td>计划</td>
              <td>状态</td>
              <td>被创建</td>
              <td>角色</td>
              <td>提供者</td>
              <td>追踪</td>
              <td>追踪结束原因</td>
              <td>操作</td>
            </tr>
          </thead>
          <tbody>
            {workspaceList.map((item: any) => {
              return (
                <tr
                  className={'border-b border-gray-200 h-12 hover:bg-gray-50 cursor-pointer'}
                >
                  <td>{item.name}</td>
                  <td>{item.plan}</td>
                  <td>{item.status}</td>
                  <td>{item.created_at}</td>
                  <td>{item.role}</td>
                  <td>{item.providers}</td>
                  <td>{item.in_trail}</td>
                  <td>{item.trial_end_reason}</td>
                  <td>
                    <div className={style.createBtn}>
                      <button type="button" onClick={() => onChecked(item)}>查看关联用户</button>
                      <button type="button" onClick={() => onConnected(item)}>关联用户</button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <div>
        {/* 页码 */}
        <Pagination
          className="flex items-center w-full h-10 text-sm select-none mt-8"
          currentPage={currPage}
          edgePageCount={2}
          middlePagesSiblingCount={1}
          setCurrentPage={setCurrPage}
          totalPages={Math.ceil(total / limit)}
          truncableClassName="w-8 px-0.5 text-center"
          truncableText="..."
        >
          <Pagination.PrevButton
            disabled={currPage === 0}
            className={`flex items-center mr-2 text-gray-500  focus:outline-none ${currPage === 0 ? 'cursor-not-allowed opacity-50' : 'cursor-pointer hover:text-gray-600 dark:hover:text-gray-200'}`} >
            <ArrowLeftIcon className="mr-3 h-3 w-3" />
            {t('appLog.table.pagination.previous')}
          </Pagination.PrevButton>
          <div className={`flex items-center justify-center flex-grow ${style.pagination}`}>
            <Pagination.PageButton
              activeClassName="bg-primary-50 dark:bg-opacity-0 text-primary-600 dark:text-white"
              className="flex items-center justify-center h-12 w-8 rounded-full cursor-pointer"
              inactiveClassName="text-gray-500"
            />
          </div>
          <Pagination.NextButton
            disabled={currPage === Math.ceil(total / limit) - 1}
            className={`flex items-center mr-2 text-gray-500 focus:outline-none ${currPage === Math.ceil(total / limit) - 1 ? 'cursor-not-allowed opacity-50' : 'cursor-pointer hover:text-gray-600 dark:hover:text-gray-200'}`} >
            {t('appLog.table.pagination.next')}
            <ArrowRightIcon className="ml-3 h-3 w-3" />
          </Pagination.NextButton>
        </Pagination>
      </div>
      <AddWorkspaceDialog show={showAddWorkspaceDialog} onClose={() => setShowAddWorkspaceDialog(false)} onSuccess={() => onSuccess()} />
      <CheckedDialog dataList={checkedList} show={showCheckedDialog} onClose={() => setShowCheckedDialog(false)} />
      <ConnectedDialog dataList={connectedList} show={showConnectedDialog} onClose={() => setShowConnectedDialog(false)} onSuccess={() => onConnectedSuc()} />
    </div>
  )
}

export default React.memo(Workspace)
