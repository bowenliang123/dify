'use client'
import React, { useEffect, useState } from 'react'
import classNames from 'classnames'
import { ArrowLeftIcon, ArrowRightIcon } from '@heroicons/react/24/outline'
import { Pagination } from 'react-headless-pagination'
import { useTranslation } from 'react-i18next'
import { useContext } from 'use-context-selector'
import style from './users.module.css'
import AddUsersDialog from './AddUsersDialog'
import { ToastContext } from '@/app/components/base/toast'
import { getList } from '@/service/users'

const Users = () => {
  const { notify } = useContext(ToastContext)
  const { t } = useTranslation()

  const [usersList, setUsersList] = useState([])
  const [currPage, setCurrPage] = useState(0)
  const [total, setTotal] = useState(0)
  const [limit, setLimit] = useState(10)
  const [showAddUsersDialog, setShowAddUsersDialog] = useState(false)

  const getLists = async (params: { page: number; limit: number }) => {
    const { data, limit, total }: any = await getList(params)
    setUsersList(data)
    setLimit(limit)
    setTotal(total)
  }

  useEffect(() => {
    getLists({ page: currPage + 1, limit })
  }, [currPage])

  const onCreate = async () => {
    setShowAddUsersDialog(true)
  }

  const onSuccess = () => {
    setShowAddUsersDialog(false)
    notify({ type: 'success', message: '新增用户成功' })
    setCurrPage(0)
  }
  return (
    <div className={classNames(style.usersStyle, 'border-t')}>
      <div className={style.createBtn}>
        <button type="button" onClick={() => onCreate()}>新增用户</button>
      </div>
      <div className={style.tableStyle}>
        {/* 表格 */}
        <table>
          <thead className="h-12 leading-8 border-b  border-gray-200 text-gray-500 font-bold">
            <tr>
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
            {usersList.map((item: any) => {
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
      <AddUsersDialog show={showAddUsersDialog} onClose={() => setShowAddUsersDialog(false)} onSuccess={() => onSuccess()} />
    </div>
  )
}

export default React.memo(Users)
